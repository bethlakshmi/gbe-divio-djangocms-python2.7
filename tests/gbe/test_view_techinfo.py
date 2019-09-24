from django.core.urlresolvers import reverse
import nose.tools as nt
from django.test import TestCase, Client
from django.test.client import RequestFactory
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from tests.contexts import (
    ActTechInfoContext,
)
from tests.functions.scheduler_functions import assert_link
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from expo.settings import DATETIME_FORMAT
from django.utils.formats import date_format


class TestReports(TestCase):
    '''Tests for index view'''
    view_name = 'view_techinfo'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.url = reverse(
            self.view_name,
            urlconf='gbe.reporting.urls')
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Tech Crew')

    def test_view_techinfo_fail(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_view_techinfo_succeed(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_view_techinfo_has_datatable(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        context = ActTechInfoContext()
        login_as(self.privileged_user, self)
        args = {'conf_slug': context.conference.conference_slug,
                'show_id': context.show.eventitem_id}

        response = self.client.get(self.url, args)

        nt.assert_true(
            "var table = $('#bid_review').DataTable({" in response.content,
            msg="Can't find script for table")
        nt.assert_true(
            '<table id="bid_review" class="order-column"'
            in response.content,
            msg="Can't find table header")
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_view_techinfo_has_rehearsal(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        context = ActTechInfoContext(schedule_rehearsal=True)
        login_as(self.privileged_user, self)
        args = {'conf_slug': context.conference.conference_slug,
                'show_id': context.show.eventitem_id,
                'area': 'stage_mgmt'}

        response = self.client.get(self.url, args)
        assert (len(context.act.get_scheduled_rehearsals()) > 0)
        for rehearsal in context.act.get_scheduled_rehearsals():
            self.assertContains(
                response,
                date_format(
                    rehearsal.start_time, "DATETIME_FORMAT"))

    def test_view_techinfo_audio(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        context = ActTechInfoContext()
        login_as(self.privileged_user, self)
        args = {'conf_slug': context.conference.conference_slug,
                'show_id': context.show.eventitem_id,
                'area': 'audio'}

        response = self.client.get(self.url, args)
        nt.assert_true(
            "var table = $('#bid_review').DataTable({" in response.content,
            msg="Can't find script for table")
        nt.assert_true(
            '<table id="bid_review" class="order-column"'
            in response.content,
            msg="Can't find table header")
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_view_techinfo_w_theater(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        context = ActTechInfoContext(room_name="Theater")
        login_as(self.privileged_user, self)
        args = {'conf_slug': context.conference.conference_slug,
                'show_id': context.show.eventitem_id,
                'area': 'lighting'}

        response = self.client.get(self.url, args)
        self.assertContains(response, 'Center Spot')

    def test_view_techinfo_has_link_for_scheduler(self):
        '''review_act_techinfo view should show schedule acts if user
            has the right privilege
        '''
        context = ActTechInfoContext()
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_user, self)
        args = {'conf_slug': context.conference.conference_slug,
                'show_id': context.show.eventitem_id}
        response = self.client.get(self.url, args)
        assert_link(response, reverse(
            'schedule_acts',
            urlconf='scheduler.urls',
            args=[context.show.pk]))
        self.assertContains(response, 'Schedule Acts for this Show')

    def test_view_techinfo_with_conference_slug(self):
        '''review_act_techinfo view show correct events for slug
        '''
        context = ActTechInfoContext()
        login_as(self.privileged_user, self)
        args = {'conf_slug': context.conference.conference_slug}
        response = self.client.get(self.url, args)
        self.assertEqual(response.status_code, 200)
        nt.assert_true(context.show.e_title in response.content)
