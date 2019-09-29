from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ActCastingOptionFactory,
    ClassFactory,
    ConferenceFactory,
    ProfileFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    LabelFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from django.test import (
    Client,
    TestCase,
)
from tests.contexts import (
    ActTechInfoContext,
    ClassContext,
    ShowContext,
)
from gbe.models import Conference
from scheduler.models import EventItem
from tests.functions.gbe_functions import (
    bad_id_for,
    login_as,
    set_image,
)
from django.contrib.auth.models import User
from datetime import (
    datetime,
    timedelta,
)


class TestEventDetailView(TestCase):
    view_name = 'detail_view'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.context = ActTechInfoContext()
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.show.eventitem_id])

    def test_no_permission_required(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.context.show.e_title)

    def test_bad_id_raises_404(self):
        bad_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[bad_id_for(EventItem)])
        response = self.client.get(bad_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_unsched_class(self):
        bid_class = ClassFactory()
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[bid_class.eventitem_id]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.content.count(bid_class.teacher.name))

    def test_repeated_lead_shows_once(self):
        show = ShowFactory()
        sched_events = [
            SchedEventFactory.create(
                eventitem=show.eventitem_ptr) for i in range(2)]
        staff_lead = ProfileFactory()
        lead_worker = WorkerFactory(_item=staff_lead.workeritem_ptr,
                                    role="Staff Lead")
        for se in sched_events:
            ResourceAllocationFactory.create(event=se,
                                             resource=lead_worker)
        response = self.client.get(reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[show.eventitem_id]))
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, response.content.count(staff_lead.display_name))

    def test_bio_grid(self):
        self.context.performer.homepage = "www.testhomepage.com"
        self.context.performer.save()
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.context.performer.homepage)

    def test_feature_performers(self):
        ActCastingOptionFactory(casting="Regular Act",
                                show_as_special=False,
                                display_order=0)
        ActCastingOptionFactory(display_order=1)

        context = ActTechInfoContext(act_role="Hosted By...")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.show.eventitem_id])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, context.performer.name)
        self.assertContains(response, "Hosted By...")

    def test_bio_grid_for_admin(self):
        superuser = User.objects.create_superuser('test_bio_grid_editor',
                                                  'admin@importimage.com',
                                                  'secret')
        ProfileFactory(user_object=superuser)
        login_as(superuser, self)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/gbe/performer/%d" % self.context.performer.pk)

    def test_feature_grid_for_admin(self):
        ActCastingOptionFactory(casting="Regular Act",
                                show_as_special=False,
                                display_order=0)
        ActCastingOptionFactory(display_order=1)

        context = ActTechInfoContext(act_role="Hosted By...")
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.show.eventitem_id])
        superuser = User.objects.create_superuser('test_feature_editor',
                                                  'admin@importimage.com',
                                                  'secret')
        ProfileFactory(user_object=superuser)
        set_image(context.performer)
        login_as(superuser, self)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/gbe/performer/%d" % context.performer.pk)

    def test_bio_grid_for_admin_w_image(self):
        superuser = User.objects.create_superuser('test_bio_grid_img_editor',
                                                  'admin@importimage.com',
                                                  'secret')
        ProfileFactory(user_object=superuser)
        login_as(superuser, self)
        set_image(self.context.performer)
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/filer/image/%d/?_pick=file&_popup=1" % (
                self.context.performer.img.pk))

    def test_feature_grid_for_admin_w_image(self):
        ActCastingOptionFactory(casting="Regular Act",
                                show_as_special=False,
                                display_order=0)
        ActCastingOptionFactory(display_order=1)

        context = ActTechInfoContext(act_role="Hosted By...")
        set_image(context.performer)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[context.show.eventitem_id])
        superuser = User.objects.create_superuser('test_feature_img_editor',
                                                  'admin@importimage.com',
                                                  'secret')
        ProfileFactory(user_object=superuser)
        login_as(superuser, self)
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertContains(
            response,
            "/admin/filer/image/%d/?_pick=file&_popup=1" % (
                context.performer.img.pk))

    def test_interested_in_event(self):
        context = ShowContext()
        interested_profile = context.set_interest()
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.show.eventitem_id])
        login_as(interested_profile, self)
        response = self.client.get(url)
        set_fav_link = reverse(
            "set_favorite",
            args=[context.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            set_fav_link,
            url))

    def test_not_really_interested_in_event(self):
        context = ShowContext()
        interested_profile = ProfileFactory()
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.show.eventitem_id])
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
            args=[context.show.eventitem_id])
        login_as(context.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertContains(
            response,
            'detail_link-disabled cal-favorite detail_link-detail_disable')

    def test_interest_not_shown(self):
        context = ShowContext(
            conference=ConferenceFactory(status="completed"))
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.show.eventitem_id])
        login_as(context.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertNotContains(response, 'fa-star')
        self.assertNotContains(response, 'fa-star-o')

    def test_eval_class(self):
        context = ClassContext(starttime=datetime.now()-timedelta(days=1))
        context.setup_eval()
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.bid.eventitem_id])
        response = self.client.get(url)
        eval_link = reverse(
            "eval_event",
            args=[context.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            eval_link,
            url))

    def test_class_already_evaled(self):
        context = ClassContext(starttime=datetime.now()-timedelta(days=1))
        eval_profile = context.set_eval_answerer()
        login_as(eval_profile, self)
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[context.bid.eventitem_id])
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
            args=[context.bid.eventitem_id])
        response = self.client.get(url)
        self.assertNotContains(response, "fa-tachometer")
