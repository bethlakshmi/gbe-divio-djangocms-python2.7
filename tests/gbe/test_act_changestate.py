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

    def test_act_changestate_authorized_user(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      args=[act.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        self.assertEqual(response.status_code, 302)

    def test_act_changestate_post_accepted_act(self):
        prev_count2 = ResourceAllocation.objects.filter(
            event=self.sched_event).count()
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data=self.data)
        self.assertEqual(1,
                        ResourceAllocation.objects.filter(
                            event=self.sched_event).count() - prev_count2)

    def test_act_changestate_unauthorized_user(self):
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')

        login_as(ProfileFactory(), self)
        response = self.client.post(url,
                                    data=self.data)

        self.assertEqual(403, response.status_code)

    def test_act_changestate_book_act_with_conflict(self):
        grant_privilege(self.privileged_user, 'Act Reviewers')
        conflict = SchedEventFactory(
            starttime=self.context.sched_event.starttime)
        ResourceAllocationFactory(
            event=conflict,
            resource=WorkerFactory(
                _item=self.context.performer.performer_profile)
        )
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data=self.data,
                                    follow=True)
        self.assertContains(
            response,
            "is booked for"
        )

    def test_act_waitlist_sends_notification_makes_template(self):
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        assert_email_template_create(
            'act wait list',
            "Your act proposal has changed status to Wait List"
        )

    def test_act_waitlist_sends_notification_has_template(self):
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act wait list',
            template__subject="test template"
        )
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data=self.data)
        assert_email_template_used(
            "test template", "actemail@notify.com")

    def test_act_accept_makes_template_per_show(self):
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(url, data=self.data)
        assert_email_template_create(
            'act accepted - %s' % self.show.e_title.lower(),
            "Your act has been cast in %s" % self.show.e_title
        )

    def test_act_accept_has_template_per_show(self):
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act accepted - %s' % self.show.e_title.lower(),
            template__subject="test template"
        )
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(url, data=self.data)
        assert_email_template_used(
            "test template", "actemail@notify.com")
        assert_email_recipient([(
            self.context.performer.contact.contact_email)])

    def test_act_accept_notification_template_fail(self):
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act accepted - %s' % self.show.e_title.lower(),
            template__subject="test template {% url 'gbehome' %}"
        )
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(url, data=self.data, follow=True)
        self.assertContains(response,
                            bidder_email_fail_msg)

    def test_act_accept_act_link_correct(self):
        EmailTemplateSenderFactory(
            from_email="actemail@notify.com",
            template__name='act accepted - %s' % self.show.e_title.lower(),
            template__subject="test template",
            template__content="stuff {{ act_tech_link }} more stuff"
        )
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(url, data=self.data)
        assert_email_contents(reverse(
            'act_tech_wizard',
            args=[self.context.act.pk],
            urlconf='gbe.urls'))

    @override_settings(ADMINS=[('Admin', 'admin@mock.test')])
    @override_settings(DEBUG=True)
    def test_act_accept_sends_debug_to_admin(self):
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        self.data['accepted'] = '3'
        response = self.client.post(url, data=self.data)
        assert_email_recipient([('admin@mock.test')])

    def test_act_special_role(self):
        ActCastingOptionFactory()
        new_context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = self.data
        data['casting'] = "Hosted by..."
        data['accepted'] = 3
        response = self.client.post(url,
                                    data=self.data,
                                    follow=True)
        casting = ActResource.objects.get(_item=self.context.act)
        assert(casting.role == data['casting'])
        self.assertRedirects(response, reverse(
            'act_review_list',
            urlconf='gbe.urls'))

    def test_act_bad_role(self):
        UserMessage.objects.all().delete()

        ActCastingOptionFactory()
        new_context = ActTechInfoContext()
        url = reverse(self.view_name,
                      args=[self.context.act.pk],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        data = self.data
        data['casting'] = "I'm a bad role"
        response = self.client.post(url,
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
