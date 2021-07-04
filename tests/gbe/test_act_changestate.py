from django.test import (
    Client,
    TestCase,
)
from django.test.utils import override_settings
from django.urls import reverse
from tests.factories.gbe_factories import (
    ActCastingOptionFactory,
    ActFactory,
    EmailTemplateSenderFactory,
    PersonaFactory,
    ProfileFactory,
    ShowFactory,
    TroupeFactory,
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
    WorkerFactory,
)
from tests.contexts import ActTechInfoContext
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_email_contents,
    assert_email_recipient,
    assert_email_template_create,
    assert_email_template_used,
    grant_privilege,
    login_as,
)
from scheduler.models import (
    Ordering,
    ResourceAllocation,
)
from gbe.models import UserMessage
from gbetext import (
    act_status_change_msg,
    act_status_no_change_msg,
    bidder_email_fail_msg,
    no_casting_msg,
)


class TestActChangestate(TestCase):
    '''Tests for act_changestate view'''
    view_name = 'act_changestate'

    def setUp(self):
        self.client = Client()
        self.context = ActTechInfoContext()
        self.show = ShowFactory(e_conference=self.context.conference)
        self.sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr)
        EventLabelFactory(event=self.sched_event,
                          text=self.context.conference.conference_slug)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Act Coordinator')
        grant_privilege(self.privileged_user, 'Act Reviewers')
        self.data = {'show': self.show.eventitem_id,
                     'casting': 'Regular Act',
                     'accepted': '2'}
        self.url = reverse(self.view_name,
                           args=[self.context.act.pk],
                           urlconf='gbe.urls')
        self.regular_casting = ActCastingOptionFactory(
            casting="Regular Act",
            show_as_special=False,
            display_header="Check Out these Performers",
            display_order=1)

    def test_act_accept_to_wait_same_show(self):
        # accepted -> waitlisted
        # same show, change role, remove rehearsal
        rehearsal_event = self.context._schedule_rehearsal(
            self.context.sched_event,
            act=self.context.act)
        login_as(self.privileged_user, self)
        data = {
            'casting': "",
            'accepted': 2,
            'show': self.context.show.eventitem_id,
        }
        response = self.client.post(self.url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))
        with self.assertRaises(ResourceAllocation.DoesNotExist):
            self.assertEqual(ResourceAllocation.objects.get(
                event=rehearsal_event))
        assert_alert_exists(
            response,
            'success',
            'Success',
            "%s<br>Performer/Act: %s - %s<br>State: %s<br>Show: %s" % (
                act_status_change_msg,
                self.context.act.performer.name,
                self.context.act.b_title,
                "Wait List",
                self.context.show.e_title))

    def test_act_keep_everything(self):
        # accepted -> accepted
        # same show, change role, keep rehearsal
        rehearsal_event = self.context._schedule_rehearsal(
            self.context.sched_event,
            act=self.context.act)
        login_as(self.privileged_user, self)
        data = {
            'casting': "Regular Act",
            'accepted': 3,
            'show': self.context.show.eventitem_id,
        }
        response = self.client.post(self.url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))
        self.assertEqual(ResourceAllocation.objects.filter(
            event=rehearsal_event).count(), 1)
        self.assertEqual(ResourceAllocation.objects.filter(
            event=self.context.sched_event).count(), 2)
        self.assertContains(response, act_status_no_change_msg)

    def test_act_change_role_keep_rehearsal(self):
        # accepted -> accepted
        # same show, change role, keep rehearsal
        rehearsal_event = self.context._schedule_rehearsal(
            self.context.sched_event,
            act=self.context.act)
        ActCastingOptionFactory()
        login_as(self.privileged_user, self)
        data = {
            'casting': "Hosted by...",
            'accepted': 3,
            'show': self.context.show.eventitem_id,
        }
        response = self.client.post(self.url,
                                    data=data,
                                    follow=True)
        casting = Ordering.objects.get(class_id=self.context.act.pk,
                                       role="Hosted by...")
        assert(casting.role == data['casting'])
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))
        self.assertEqual(ResourceAllocation.objects.filter(
                event=rehearsal_event).count(), 1)
        self.assertEqual(ResourceAllocation.objects.filter(
                event=self.context.sched_event).count(), 2)

    def test_act_withdrawl(self):
        # accepted -> withdrawn
        # remove all act bookings
        rehearsal_event = self.context._schedule_rehearsal(
            self.context.sched_event,
            act=self.context.act)

        login_as(self.privileged_user, self)
        data = {
            'accepted': 4,
        }
        response = self.client.post(self.url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))

        with self.assertRaises(ResourceAllocation.DoesNotExist):
            rehearsal_booking = ResourceAllocation.objects.get(
                event=rehearsal_event)
        self.assertEqual(1, ResourceAllocation.objects.filter(
                event=self.context.sched_event).count())
        booking = ResourceAllocation.objects.get(
                event=self.context.sched_event)
        self.assertEqual(booking.resource.item.as_subtype,
                         self.context.room)
        assert_alert_exists(
            response,
            'success',
            'Success',
            "%s<br>Performer/Act: %s - %s<br>State: %s" % (
                act_status_change_msg,
                self.context.act.performer.name,
                self.context.act.b_title,
                "Withdrawn"))

    def test_act_withdraw_redirect(self):
        # accepted -> withdrawn
        # show alert, but redirect to the identified page
        grant_privilege(self.privileged_user, 'Technical Director')
        login_as(self.privileged_user, self)
        next_url = reverse(
            'show_dashboard',
            urlconf='gbe.scheduling.urls',
            args=[self.sched_event.pk])
        data = {
            'accepted': 4,
            'next': next_url,
        }
        response = self.client.post(self.url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(response, next_url)

        assert_alert_exists(
            response,
            'success',
            'Success',
            "%s<br>Performer/Act: %s - %s<br>State: %s" % (
                act_status_change_msg,
                self.context.act.performer.name,
                self.context.act.b_title,
                "Withdrawn"))

    def test_act_accept_act_link_correct(self):
        # accepted -> accepted
        # change show, loose rehearsal
        # same role
        rehearsal_event = self.context._schedule_rehearsal(
            self.context.sched_event,
            act=self.context.act)
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act accepted - %s' % self.show.e_title.lower(),
            template__subject="test template",
            template__content="stuff {{ act_tech_link }} more stuff"
        )
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'

        response = self.client.post(self.url, data=self.data, follow=True)
        assert_email_contents(reverse(
            'act_tech_wizard',
            args=[self.context.act.pk],
            urlconf='gbe.urls'))
        with self.assertRaises(ResourceAllocation.DoesNotExist):
            rehearsal_booking = ResourceAllocation.objects.get(
                event=rehearsal_event)
        assert_alert_exists(
            response,
            'success',
            'Success',
            "%s<br>Performer/Act: %s - %s<br>State: %s<br>Show: %s" % (
                act_status_change_msg,
                self.context.act.performer.name,
                self.context.act.b_title,
                "Accepted",
                self.show.e_title))

    def test_act_changestate_authorized_user(self):
        # No decision -> waitlist
        # new show, new role
        act = ActFactory(b_conference=self.context.conference)
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        self.assertEqual(response.status_code, 302)
        assert_email_template_create(
            'act wait list',
            "Your act proposal has changed status to Wait List"
        )
        casting = Ordering.objects.get(class_id=act.pk)
        assert(casting.role == "Waitlisted")

    def test_act_changestate_troupe(self):
        # No decision -> accept
        # new show, new role
        act = ActFactory(b_conference=self.context.conference,
                         performer=TroupeFactory())
        act.performer.membership.add(PersonaFactory())
        act.performer.membership.add(PersonaFactory())

        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        self.data['accepted'] = '3'
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data, follow=True)
        self.assertContains(response, "%s<br>Performer/Act: %s " % (
            act_status_change_msg,
            str(act.performer)))

    def test_act_changestate_post_waitlisted_act(self):
        # accepted -> waitlist
        # change show, change role
        rehearsal_event = self.context._schedule_rehearsal(
            self.context.sched_event,
            act=self.context.act)
        prev_count2 = ResourceAllocation.objects.filter(
            event=self.sched_event).count()
        login_as(self.privileged_user, self)
        response = self.client.post(self.url,
                                    data=self.data)
        self.assertEqual(1,
                         ResourceAllocation.objects.filter(
                            event=self.sched_event).count() - prev_count2)
        assert_email_template_create(
            'act wait list',
            "Your act proposal has changed status to Wait List"
        )
        casting = Ordering.objects.get(class_id=self.context.act.pk)
        assert(casting.role == "Waitlisted")
        with self.assertRaises(ResourceAllocation.DoesNotExist):
            ResourceAllocation.objects.get(event=rehearsal_event)

    def test_act_changestate_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.post(self.url,
                                    data=self.data)

        self.assertEqual(403, response.status_code)

    def test_act_changestate_book_act_with_conflict(self):
        # accepted -> waitlist (#2, see above)
        # change show, change role
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act wait list',
            template__subject="test template"
        )
        grant_privilege(self.privileged_user, 'Act Reviewers')
        conflict = SchedEventFactory(
            starttime=self.context.sched_event.starttime)
        EventLabelFactory(event=conflict,
                          text=self.context.conference.conference_slug)
        ResourceAllocationFactory(
            event=conflict,
            resource=WorkerFactory(
                _item=self.context.performer.performer_profile))
        login_as(self.privileged_user, self)
        response = self.client.post(self.url,
                                    data=self.data,
                                    follow=True)
        self.assertContains(
            response,
            "Conflicting booking: %s" % str(conflict))
        assert_email_template_used(
            "test template", "actemail@notify.com")

    def test_act_accept_makes_template_per_show(self):
        # waitlisted -> accepted
        # change show, same role
        self.context = ActTechInfoContext(set_waitlist=True)
        self.url = reverse(self.view_name,
                           args=[self.context.act.pk],
                           urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(self.url, data=self.data)
        assert_email_template_create(
            'act accepted - %s' % self.show.e_title.lower(),
            "Your act has been cast in %s" % self.show.e_title
        )
        casting = Ordering.objects.get(
            class_id=self.context.act.pk,
            allocation__event=self.sched_event)
        assert(casting.role == "Regular Act")

    def test_act_accept_notification_template_fail(self):
        # accepted -> accepted - error case
        # change show, same role
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act accepted - %s' % self.show.e_title.lower(),
            template__subject="test template {% url 'gbehome' %}"
        )
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(self.url, data=self.data, follow=True)
        self.assertContains(response,
                            bidder_email_fail_msg)

    @override_settings(ADMINS=[('Admin', 'admin@mock.test')])
    @override_settings(DEBUG=True)
    def test_act_accept_sends_debug_to_admin(self):
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(self.url, data=self.data)
        assert_email_recipient([('admin@mock.test')])

    def test_act_change_to_special_role(self):
        # accepted -> accepted
        # change show, change role
        ActCastingOptionFactory()
        new_context = ActTechInfoContext()
        login_as(self.privileged_user, self)
        data = self.data
        data['casting'] = "Hosted by..."
        data['accepted'] = 3
        response = self.client.post(self.url,
                                    data=data,
                                    follow=True)
        casting = Ordering.objects.get(class_id=self.context.act.pk)
        assert(casting.role == data['casting'])
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))

    def test_act_accept_and_special_role(self):
        # accepted -> accepted
        # change show, change role
        ActCastingOptionFactory()
        act = ActFactory(b_conference=self.context.conference)
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = self.data
        data['casting'] = "Hosted by..."
        data['accepted'] = 3
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        casting = Ordering.objects.get(class_id=act.pk)
        assert(casting.role == data['casting'])
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))
        assert_email_template_create(
            'act accepted - %s' % self.show.e_title.lower(),
            "Your act has been cast in %s" % self.show.e_title
        )

    def test_act_bad_role(self):
        UserMessage.objects.all().delete()
        ActCastingOptionFactory()
        new_context = ActTechInfoContext()
        login_as(self.privileged_user, self)
        data = self.data
        data['casting'] = "I'm a bad role"
        response = self.client.post(self.url,
                                    data=self.data,
                                    follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', no_casting_msg)

    def test_act_no_role(self):
        UserMessage.objects.all().delete()

        ActCastingOptionFactory()
        new_context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = self.data
        data.pop('casting', None)
        response = self.client.post(url,
                                    data=self.data,
                                    follow=True)
        assert_alert_exists(
            response, 'danger', 'Error', no_casting_msg)

    def test_act_changestate_stay_waitlisted_act(self):
        # waitlisted -> waitlisted
        # change show
        self.context = ActTechInfoContext(set_waitlist=True)
        self.url = reverse(self.view_name,
                           args=[self.context.act.pk],
                           urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(self.url,
                                    data=self.data)
        casting = Ordering.objects.get(
            class_id=self.context.act.pk,
            allocation__event=self.sched_event)
        assert(casting.role == "Waitlisted")

    def test_bad_show(self):
        # accepted -> accepted
        # change show, change role
        login_as(self.privileged_user, self)
        data = self.data
        data['show'] = self.show.eventitem_id + 1
        response = self.client.post(self.url,
                                    data=data,
                                    follow=True)
        self.assertEqual(404, response.status_code)
