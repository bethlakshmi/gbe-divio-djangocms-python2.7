from django.urls import reverse
from gbe_forms_text import difficulty_default_text
from tests.factories.gbe_factories import (
    ActCastingOptionFactory,
    ClassLabelFactory,
    ConferenceFactory,
    ProfileFactory,
)
from django.test import TestCase
from tests.contexts import (
    ActTechInfoContext,
    ClassContext,
    ShowContext,
    StaffAreaContext,
)
from gbe.models import Conference
from scheduler.models import Event
from tests.functions.gbe_functions import (
    bad_id_for,
    login_as,
    set_image,
    setup_admin_w_privs,
    setup_social_media,
)
from django.contrib.auth.models import User
from datetime import (
    datetime,
    timedelta,
)
from gbetext import (
    login_please,
    paired_alert_msg,
    pending_note,
)


class TestEventDetailView(TestCase):
    view_name = 'detail_view'

    @classmethod
    def setUpTestData(cls):
        cls.regular_casting = ActCastingOptionFactory(
            casting="Regular Act",
            show_as_special=False,
            display_header="Check Out these Performers",
            display_order=0)
        Conference.objects.all().delete()
        cls.context = ActTechInfoContext()
        cls.url = reverse(
            cls.view_name,
            urlconf="gbe.scheduling.urls",
            args=[cls.context.sched_event.pk])
        cls.label = ClassLabelFactory()

    def test_no_permission_required(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.context.sched_event.title)

    def test_bad_id_raises_404(self):
        bad_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[bad_id_for(Event)])
        response = self.client.get(bad_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_location_full_room_display(self):
        self.context.room.address = "The place where I live"
        self.context.room.map_embed = \
            '<iframe src="https://www.google.com/></iframe>'
        self.context.room.save()

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.context.room.address)
        self.assertContains(response, self.context.room.map_embed)

    def test_bio_grid(self):
        another_context = ActTechInfoContext(
            sched_event=self.context.sched_event,
            conference=self.context.conference)
        link1 = another_context.set_social_media(social_network="Venmo")
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.regular_casting.display_header)
        self.assertContains(response, another_context.performer.name)
        self.assertContains(response, setup_social_media(link1))

    def test_feature_performers(self):
        ActCastingOptionFactory(display_order=1)
        context = ActTechInfoContext(act_role="Hosted by...")
        link0 = context.set_social_media()
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.sched_event.pk])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, context.performer.name)
        self.assertContains(response, "Hostest with the mostest")
        self.assertContains(response, setup_social_media(link0))

    def test_bad_casting(self):
        ActCastingOptionFactory(display_order=1)
        context = ActTechInfoContext(act_role="Weirdo")
        another_context = ActTechInfoContext(
            act_role="Weirdo",
            sched_event=context.sched_event,
            conference=context.conference)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.sched_event.pk])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, context.performer.name)
        self.assertContains(response, another_context.performer.name)
        self.assertContains(response, "Fabulous Performers")

    def test_empty_casting(self):
        ActCastingOptionFactory(display_order=1)
        context = ActTechInfoContext(act_role="")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.sched_event.pk])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, context.performer.name)
        self.assertContains(response, "Fabulous Performers")

    def test_bio_grid_for_admin(self):
        superuser = setup_admin_w_privs([])
        login_as(superuser, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/gbe/performer/%d" % self.context.performer.pk)

    def test_feature_grid_for_admin(self):
        ActCastingOptionFactory(display_order=1)

        context = ActTechInfoContext(act_role="Hosted by...")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.sched_event.pk])
        superuser = setup_admin_w_privs([])
        set_image(context.performer)
        login_as(superuser, self)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/gbe/performer/%d" % context.performer.pk)

    def test_bio_grid_for_admin_w_image(self):
        superuser = setup_admin_w_privs([])
        login_as(superuser, self)
        set_image(self.context.performer)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/filer/image/%d/?_pick=file&_popup=1" % (
                self.context.performer.img.pk))

    def test_feature_grid_for_admin_w_image(self):
        from cms.models.permissionmodels import PageUser

        ActCastingOptionFactory(display_order=1)
        context = ActTechInfoContext(act_role="Hosted by...")
        set_image(context.performer)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.sched_event.pk])
        superuser = setup_admin_w_privs([])
        login_as(superuser, self)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/filer/image/%d/?_pick=file&_popup=1" % (
                context.performer.img.pk))

    def test_interested_in_event(self):
        context = ShowContext()
        package, this_show = context.setup_tickets()
        interested_profile = context.set_interest()
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.sched_event.pk])
        login_as(interested_profile, self)
        response = self.client.get(url)
        set_fav_link = reverse(
            "set_favorite",
            args=[context.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            set_fav_link,
            url))
        self.assertContains(response, package.ticketing_event.title)
        self.assertContains(response, this_show.ticketing_event.title)

    def test_not_really_interested_in_event(self):
        context = ShowContext()
        interested_profile = ProfileFactory()
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.sched_event.pk])
        login_as(interested_profile, self)
        response = self.client.get(url)
        set_fav_link = reverse(
            "set_favorite",
            args=[context.sched_event.pk, "on"],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            set_fav_link,
            url))
        self.assertNotContains(response, "fa-tachometer")

    def test_disabled_interest(self):
        context = ShowContext()
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.sched_event.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        self.assertContains(
            response,
            'cal-favorite detail_link-detail_disable')

    def test_interest_not_shown(self):
        context = ShowContext(
            conference=ConferenceFactory(status="completed"))
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.sched_event.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        self.assertNotContains(response, 'fas fa-star')
        self.assertNotContains(response, 'far fa-star')

    def test_eval_class(self):
        context = ClassContext(starttime=datetime.now()-timedelta(days=1))
        context.setup_eval()
        context.bid.difficulty = "Easy"
        context.bid.save()
        context.bid.labels.add(self.label)
        link = context.set_social_media("CashApp")
        package, this_class = context.setup_tickets()
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.sched_event.pk])
        response = self.client.get(url)
        eval_link = reverse(
            "eval_event",
            args=[context.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            eval_link,
            url))
        self.assertContains(response, package.ticketing_event.title)
        self.assertContains(response, this_class.ticketing_event.title)
        self.assertContains(response, setup_social_media(link))
        self.assertContains(response, difficulty_default_text["Easy"])
        self.assertContains(
            response,
            '<span class="badge badge-pill gbe-badge">%s</span>' % (
                self.label.text),
            html=True)

    def test_class_already_evaled(self):
        context = ClassContext(starttime=datetime.now()-timedelta(days=1))
        eval_profile = context.set_eval_answerer()
        login_as(eval_profile, self)
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.sched_event.pk])
        response = self.client.get(url)
        eval_link = reverse(
            "eval_event",
            args=[context.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertNotContains(response, "%s?next=%s" % (
            eval_link,
            url))
        self.assertContains(response, "You have already rated this class")

    def test_no_eval_for_teacher(self):
        context = ClassContext(starttime=datetime.now()-timedelta(days=1))
        context.setup_eval()
        login_as(context.teacher.contact, self)
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.sched_event.pk])
        response = self.client.get(url)
        self.assertNotContains(response, "fa-tachometer")

    def test_volunteer_approval_pending(self):
        context = StaffAreaContext()
        volunteer, booking = context.book_volunteer(role="Pending Volunteer")
        opportunity = booking.event
        opportunity.approval_needed = True
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.save()
        login_as(volunteer, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[opportunity.pk])
        response = self.client.get(url)
        vol_link = reverse('set_volunteer',
                           args=[opportunity.pk, 'off'],
                           urlconf='gbe.scheduling.urls')
        self.assertContains(response, opportunity.title)
        self.assertContains(response, vol_link)
        self.assertContains(response, 'awaiting_approval.gif')
        self.assertContains(response, pending_note)

    def test_view_volunteers_and_links(self):
        staff_context = StaffAreaContext()
        opportunity = staff_context.add_volunteer_opp()
        linked_opportunity = staff_context.add_volunteer_opp()

        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.save()
        linked_opportunity.starttime = datetime.now() + timedelta(days=2)
        linked_opportunity.save()
        opportunity.set_peer(linked_opportunity)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[opportunity.pk])
        response = self.client.get(url)
        self.assertContains(response, opportunity.title)
        self.assertContains(response,
                            'volunteered.gif" class="volunteer-icon-large"')
        self.assertNotContains(
            response,
            reverse('set_volunteer',
                    args=[opportunity.pk, 'on'],
                    urlconf='gbe.scheduling.urls'))
        self.assertContains(response, reverse('login'))
        self.assertContains(response, reverse('register', urlconf="gbe.urls"))
        self.assertContains(response, login_please)
        self.assertContains(response, paired_alert_msg)
        self.assertContains(response, reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[linked_opportunity.pk]))
