from django.test import (
    Client,
    TestCase,
)
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ActCastingOptionFactory,
    ActFactory,
    EmailTemplateSenderFactory,
    ProfileFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
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
    ActResource,
    ResourceAllocation,
)
from gbe.models import UserMessage
from gbetext import (
    bidder_email_fail_msg,
    no_casting_msg,
)


class TestActChangestate(TestCase):
    '''Tests for act_changestate view'''
    view_name = 'act_changestate'

    def setUp(self):
        self.client = Client()
        self.context = ActTechInfoContext()
        self.show = ShowFactory()
        self.sched_event = SchedEventFactory(eventitem=self.show.eventitem_ptr)
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Act Coordinator')
        grant_privilege(self.privileged_user, 'Act Reviewers')
        self.data = {'show': self.show.eventitem_id,
                     'casting': '',
                     'accepted': '2'}
        self.url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')

    def test_act_withdrawl(self):
        # accepted -> withdrawn
        # remove all act bookings
        print ("start...")
        print (self.context.show.eventitem_id)
        print (self.context.show)
        print (self.context.sched_event.pk)
        print (self.context.sched_event)
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

        response = self.client.post(self.url, data=self.data)
        assert_email_contents(reverse(
            'act_tech_wizard',
            args=[self.context.act.pk],
            urlconf='gbe.urls'))
        with self.assertRaises(ResourceAllocation.DoesNotExist):
            rehearsal_booking = ResourceAllocation.objects.get(
                event=rehearsal_event)

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
        casting = ActResource.objects.get(_item=act)
        assert(casting.role == "Waitlisted")


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
        casting = ActResource.objects.get(_item=self.context.act)
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
        ResourceAllocationFactory(
            event=conflict,
            resource=WorkerFactory(
                _item=self.context.performer.performer_profile)
        )
        login_as(self.privileged_user, self)
        response = self.client.post(self.url,
                                    data=self.data,
                                    follow=True)
        self.assertContains(
            response,
            "is booked for"
        )
        assert_email_template_used(
            "test template", "actemail@notify.com")

    def test_act_accept_makes_template_per_show(self):
        # accepted -> accepted
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
        casting = ActResource.objects.get(_item=self.context.act)
        assert(casting.role == "")

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
        casting = ActResource.objects.get(_item=self.context.act)
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
        casting = ActResource.objects.get(_item=act)
        assert(casting.role == data['casting'])
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))
        assert_email_template_create(
            'act accepted - %s' % self.show.e_title.lower(),
            "Your act has been cast in %s" % self.show.e_title
        )

    def test_act_change_role_keep_rehearsal(self):
        # accepted -> accepted
        # same show, change role, keep rehearsal
        rehearsal_event = self.context._schedule_rehearsal(
            self.context.sched_event,
            act=self.context.act)
        ActCastingOptionFactory()
        act = ActFactory(b_conference=self.context.conference)
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = {
            'casting': "Hosted by...",
            'accepted': 3,
            'show': self.context.show.eventitem_id,
        }
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        casting = ActResource.objects.get(_item=act)
        assert(casting.role == data['casting'])
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))
        self.assertEqual(ResourceAllocation.objects.filter(
                event=rehearsal_event).count(), 1)

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
        casting = ActResource.objects.get(_item=self.context.act)
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
