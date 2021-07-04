from pytz import utc
from django.urls import reverse
from datetime import (
    datetime,
    time,
)
from django.test import TestCase, Client
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import ActTechInfoContext
from django.utils.formats import date_format


class TestReviewActTechInfo(TestCase):
    '''Tests for index view'''
    view_name = 'show_dashboard'

    def setUp(self):
        self.client = Client()
        self.context = ActTechInfoContext(schedule_rehearsal=True)
        self.other_context = ActTechInfoContext(
            conference=self.context.conference)
        self.profile = self.context.make_priv_role()
        self.url = reverse(self.view_name,
                           urlconf='gbe.scheduling.urls',
                           args=[self.context.sched_event.pk])

    def test_no_permission(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_has_datatable(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "var table = $('#gbe-table').DataTable({",
            msg_prefix="Can't find script for table")
        self.assertContains(
            response,
            '<table id="gbe-table"',
            msg_prefix="Can't find table header")
        self.assertContains(response, self.context.act.b_title)
        self.assertContains(response, self.url)
        self.assertNotContains(response, reverse(
            self.view_name,
            urlconf='gbe.scheduling.urls',
            args=[self.other_context.sched_event.pk]))
        self.assertContains(response, reverse(
            "act_tech_wizard",
            urlconf='gbe.urls',
            args=[self.context.act.id]))
        self.assertContains(response, date_format(
            self.context.rehearsal.start_time,
            "DATETIME_FORMAT"))
        self.assertContains(
            response,
            ('<input type="number" name="%d-order" value="%d" ' +
             'style="width: 3.5em" required id="id_%d-order">') % (
             self.context.booking.pk,
             self.context.order.order,
             self.context.booking.pk),
            html=True)

    def test_no_techinfo_no_order_change(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        self.context.order_act(self.context.act, "3")
        self.profile = ProfileFactory()
        grant_privilege(self.profile, 'Act Coordinator')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.context.act.b_title)
        self.assertNotContains(response, reverse(
            "act_tech_wizard",
            urlconf='gbe.urls',
            args=[self.context.act.id]))
        self.assertContains(
            response,
            "<td data-order=\'3\'>\n        3\n      </td>")

    def test_review_act_techinfo_show_inactive(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        self.context.act.performer.contact.user_object.is_active = False
        self.context.act.performer.contact.user_object.save()

        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "- INACTIVE",
            msg_prefix="Can't find inactive user")

    def test_review_act_techinfo_has_video(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        video_act = self.context.act
        video_act.video_link = "http://www.test.com"
        video_act.video_choice = 2
        video_act.save()
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, video_act.video_link)

    def test_review_act_techinfo_rebook_perm(self):
        self.profile = self.context.make_priv_role('Producer')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, reverse(
            "act_changestate",
            urlconf="gbe.urls",
            args=[self.context.act.id]))

    def test_cross_show(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        self.profile = ProfileFactory()
        grant_privilege(self.profile, 'Scheduling Mavens')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.context.act.b_title)
        self.assertNotContains(response, reverse(
            "act_tech_wizard",
            urlconf='gbe.urls',
            args=[self.context.act.id]))
        print(response.content)
        self.assertContains(response, reverse(
            self.view_name,
            urlconf='gbe.scheduling.urls',
            args=[self.other_context.sched_event.pk]))
