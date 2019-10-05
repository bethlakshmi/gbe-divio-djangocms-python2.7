from pytz import utc
from django.core.urlresolvers import reverse
from datetime import (
    datetime,
    time,
)
from django.test import TestCase, Client
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceDayFactory,
    ConferenceFactory,
    ProfileFactory,
    ShowFactory,
)
from tests.factories.scheduler_factories import (
    ActResourceFactory,
    ResourceAllocationFactory,
    SchedEventFactory,
)
from tests.functions.scheduler_functions import assert_link
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


def _create_scheduled_show_with_acts(conference=None, qty=6):
    if not conference:
        conference = ConferenceFactory()
    conf_day = ConferenceDayFactory(
        conference=conference)

    show = ShowFactory(e_conference=conference)
    sEvent = SchedEventFactory(
        eventitem=show.eventitem_ptr,
        starttime=utc.localize(datetime.combine(conf_day.day, time(20, 0))))
    acts = [ActFactory(accepted=3) for i in range(qty)]
    for act in acts:
        ar = ActResourceFactory(_item=act.actitem_ptr)
        ResourceAllocationFactory(
            event=sEvent,
            resource=ar)
    return show, sEvent, acts


class TestReports(TestCase):
    '''Tests for index view'''
    view_name = 'act_techinfo_review'

    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()
        grant_privilege(self.profile, 'Tech Crew')

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

    def test_review_act_techinfo_succeed(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Schedule Acts for this Show')

    def test_review_act_techinfo_has_datatable(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[curr_show.eventitem_id]))
        self.assertTrue(
            "var table = $('#bid_review').DataTable({" in response.content,
            msg="Can't find script for table")
        self.assertTrue(
            '<table id="bid_review" class="order-column"'
            in response.content,
            msg="Can't find table header")
        self.assertNotContains(response, 'Schedule Acts for this Show')
        for act in curr_acts:
            self.assertTrue(act.b_title in response.content)

    def test_review_act_techinfo_show_inactive(self):
        '''review_act_techinfo view should show data when show is
            selected
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        curr_acts[0].performer.contact.user_object.is_active = False
        curr_acts[0].performer.contact.user_object.save()

        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[curr_show.eventitem_id]))
        self.assertTrue(
            "- INACTIVE" in response.content,
            msg="Can't find inactive user")

    def test_review_act_techinfo_has_link_for_scheduler(self):
        '''review_act_techinfo view should show schedule acts if user
            has the right privilege
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        grant_privilege(self.profile, 'Scheduling Mavens')
        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls',
                    args=[curr_show.eventitem_id]),
            data={'conf_slug': curr_conf.conference_slug})
        assert_link(response, reverse(
            'schedule_acts',
            urlconf='scheduler.urls',
            args=[curr_show.pk]))
        self.assertContains(response, 'Schedule Acts for this Show')

    def test_review_act_techinfo_with_conference_slug(self):
        '''review_act_techinfo view show correct events for slug
        '''
        curr_conf = ConferenceFactory()
        curr_show, _, curr_acts = _create_scheduled_show_with_acts(curr_conf)
        old_conf = ConferenceFactory(status='completed')
        old_show, _, old_acts = _create_scheduled_show_with_acts(old_conf)

        login_as(self.profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.reporting.urls'),
            data={'conf_slug': curr_conf.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(curr_show.e_title in response.content)
