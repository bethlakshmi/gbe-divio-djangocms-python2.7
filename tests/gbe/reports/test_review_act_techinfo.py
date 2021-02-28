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
    view_name = 'act_techinfo_review'

    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()
        grant_privilege(self.profile, 'Tech Crew')
        self.context = ActTechInfoContext(schedule_rehearsal=True)

    def test_review_act_techinfo_fail(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(
            reverse('act_techinfo_review',
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 403)

    def test_review_act_techinfo_no_show_picked(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.conference.conference_slug)
        self.assertContains(response, str(self.context.show))
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_review_act_techinfo_has_datatable(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[self.context.show.eventitem_id]))
        self.assertContains(
            response,
            "var table = $('#gbe-table').DataTable({",
            msg_prefix="Can't find script for table")
        self.assertContains(
            response,
            '<table id="gbe-table"',
            msg_prefix="Can't find table header")
        self.assertNotContains(response, 'Schedule Acts for this Show')
        self.assertContains(response, self.context.act.b_title)
        self.assertNotContains(response, reverse(
            "act_tech_wizard",
            urlconf='gbe.urls',
            args=[self.context.act.id]))
        self.assertContains(response, date_format(
            self.context.rehearsal.start_time,
            "DATETIME_FORMAT"))

    def test_review_act_techinfo_show_inactive(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        self.context.act.performer.contact.user_object.is_active = False
        self.context.act.performer.contact.user_object.save()

        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[self.context.show.eventitem_id]))
        self.assertContains(
            response,
            "- INACTIVE",
            msg_prefix="Can't find inactive user")

    def test_review_act_techinfo_has_link_for_scheduler(self):
        '''review_act_techinfo view should show schedule acts if user
            has the right privilege
        '''
        grant_privilege(self.profile, 'Scheduling Mavens')
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[self.context.show.eventitem_id]),
            data={'conf_slug': self.context.conference.conference_slug})
        self.assertContains(response, 'Schedule Acts for this Show')
        self.assertContains(response, reverse(
            'schedule_acts',
            urlconf='gbe.scheduling.urls',
            args=[self.context.show.eventitem_id]))

    def test_review_act_techinfo_with_conference_slug(self):
        '''review_act_techinfo view show correct events for slug
        '''
        old_conf = ConferenceFactory(status='completed')
        old_context = ActTechInfoContext(conference=old_conf)

        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls'),
            data={'conf_slug': self.context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.show.e_title)
        self.assertNotContains(response, old_context.show.e_title)

    def test_review_act_techinfo_has_video(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        video_act = self.context.act
        video_act.video_link = "http://www.test.com"
        video_act.video_choice = 2
        video_act.save()
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[self.context.show.eventitem_id]))
        self.assertContains(response, video_act.video_link)

    def test_review_act_techinfo_has_link_for_editing(self):
        '''review_act_techinfo view should show schedule acts if user
            has the right privilege
        '''
        grant_privilege(self.profile, 'Technical Director')
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[self.context.show.eventitem_id]),
            data={'conf_slug': self.context.conference.conference_slug})
        self.assertContains(response, self.context.act.b_title)
        self.assertContains(response, reverse(
            "act_tech_wizard",
            urlconf='gbe.urls',
            args=[self.context.act.id]))

    def test_review_with_order(self):
        self.context.order_act(self.context.act, "3")
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[self.context.show.eventitem_id]),
            data={'conf_slug': self.context.conference.conference_slug})
        self.assertContains(response, '<td>3</td>', html=True)
