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
    TechInfoFactory,
)
from tests.factories.scheduler_factories import EventLabelFactory
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    ActTechInfoContext,
    ShowContext,
    StaffAreaContext,
    VolunteerContext,
)
from django.utils.formats import date_format
from gbetext import (
    act_order_form_invalid,
    act_order_submit_success,
    no_scope_error,
)


class TestShowDashboard(TestCase):
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

    def get_basic_post(self, order_value=1):
        data = {
            "%d-order" % self.context.booking.pk: order_value}
        return data

    def test_no_permission(self):
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_bad_show(self):
        login_as(self.profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.other_context.sched_event.pk+100])
        response = self.client.get(bad_url, follow=True)
        self.assertContains(
            response,
            "OCCURRENCE_NOT_FOUND  Occurrence id %d not found" % (
                self.other_context.sched_event.pk+100))

    def test_not_this_show(self):
        '''Stage Managers get to update act tech, volunteers, and act order
        '''
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.url = reverse(self.view_name,
                           urlconf='gbe.scheduling.urls',
                           args=[self.other_context.sched_event.pk])
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, no_scope_error)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))

    def test_has_datatable(self):
        '''Stage Managers get to update act tech, volunteers, and act order
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

    def test_no_techinfo_edit_no_order_change(self):
        '''Act Coordinator can't edit act tech, or the order
        This should be an act w/out tech info.
        '''
        self.context.order_act(self.context.act, "3")
        self.profile = ProfileFactory()
        grant_privilege(self.profile, 'Act Coordinator')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.context.act.b_title)
        self.assertContains(
            response,
            'class="gbe-table-row gbe-table-danger"',
            1)
        self.assertContains(
            response,
            '<i class="fas fa-window-close gbe-text-danger"></i>')
        self.assertNotContains(response, reverse(
            "act_tech_wizard",
            urlconf='gbe.urls',
            args=[self.context.act.id]))
        self.assertContains(
            response,
            "<td data-order=\'3\'>\n        3\n      </td>")

    def test_show_inactive(self):
        ''' show red when user is deactivated '''
        self.context.act.performer.contact.user_object.is_active = False
        self.context.act.performer.contact.user_object.save()

        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "- INACTIVE",
            msg_prefix="Can't find inactive user")

    def test_has_video(self):
        ''' view a video link if act has it. '''
        video_act = self.context.act
        video_act.video_link = "http://www.test.com"
        video_act.video_choice = 2
        video_act.save()
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, video_act.video_link)

    def test_rebook_perm(self):
        ''' Producers can book act into a different show '''
        self.profile = self.context.make_priv_role('Producer')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, reverse(
            "act_changestate",
            urlconf="gbe.urls",
            args=[self.context.act.id]))

    def test_cross_show(self):
        ''' Scheduling Mavens can see all the shows in the conference
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
        self.assertContains(response, reverse(
            self.view_name,
            urlconf='gbe.scheduling.urls',
            args=[self.other_context.sched_event.pk]))

    def test_get_show_w_no_acts(self):
        no_act_context = ShowContext()
        no_act_context.performer.delete()
        no_act_context.acts[0].delete()
        no_act_url = reverse(self.view_name,
                             urlconf="gbe.scheduling.urls",
                             args=[no_act_context.sched_event.pk])
        self.profile = ProfileFactory()
        grant_privilege(self.profile, 'Act Coordinator')
        login_as(self.profile, self)
        response = self.client.get(no_act_url)
        self.assertContains(response, "There are no available acts.")

    def test_show_volunteer(self):
        '''staff_area view should load
        '''
        vol_context = VolunteerContext(sched_event=self.context.sched_event,
                                       conference=self.context.conference)
        self.profile = ProfileFactory()
        grant_privilege(self.profile, 'Scheduling Mavens')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, vol_context.opp_event.title)
        self.assertContains(response, reverse(
            'mail_to_individual',
            urlconf='gbe.email.urls',
            args=[vol_context.profile.resourceitem_id]))
        self.assertContains(response, reverse(
            'detail_view',
            urlconf='gbe.scheduling.urls',
            args=[vol_context.opp_event.pk]))

    def test_show_with_inactive(self):
        ''' view should load
        '''
        inactive = ProfileFactory(
            display_name="Inactive User",
            user_object__is_active=False
        )
        context = VolunteerContext(sched_event=self.context.sched_event,
                                   conference=self.context.conference,
                                   profile=inactive)
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, context.opp_event.title)
        self.assertContains(
            response,
            '<div class="gbe-form-error">')
        self.assertContains(response, inactive.display_name)

    def test_complete_wout_rehearsals_act(self):
        ''' view should load
        '''
        complete_act_context = ActTechInfoContext()
        complete_act_context.act.tech = TechInfoFactory(
            confirm_no_music=True,
            confirm_no_rehearsal=True,
            prop_setup="text",
            starting_position="Onstage",
            primary_color="text",
            feel_of_act="text",
            pronouns="text",
            introduction_text="text")
        complete_act_context.act.accepted = 3
        complete_act_context.act.save()
        self.profile = complete_act_context.make_priv_role()
        login_as(self.profile, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf='gbe.scheduling.urls',
            args=[complete_act_context.sched_event.pk]))
        self.assertContains(response, complete_act_context.act.b_title)
        self.assertNotContains(
            response,
            'class="gbe-table-row gbe-table-danger"')
        self.assertContains(response, "No audio track needed")
        self.assertContains(response, "Acknowledged No Rehearsal")
        self.assertContains(
            response,
            '<i class="fas fa-check-circle gbe-text-success"></i>')
        self.assertContains(
            response, 
            ('<input type="hidden" name="event-select-events" ' +
             'value="%d" id="id_event-select-events_0">') % (
             complete_act_context.sched_event.pk),
            html=True)

    def test_show_approval_needed_event(self):
        context = VolunteerContext(sched_event=self.context.sched_event,
                                   conference=self.context.conference)
        context.opp_event.approval_needed = True
        context.opp_event.save()
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, context.opp_event.title)
        self.assertContains(response, 'class="approval_needed"')

    def test_staff_area_role_display(self):
        vol_context = VolunteerContext(sched_event=self.context.sched_event,
                                       conference=self.context.conference)
        context = StaffAreaContext(conference=self.context.conference)
        EventLabelFactory(event=vol_context.opp_event,
                          text=context.area.slug)
        vol1, opp1 = context.book_volunteer(
            volunteer_sched_event=vol_context.opp_event)
        vol2, opp2 = context.book_volunteer(
            volunteer_sched_event=vol_context.opp_event,
            role="Pending Volunteer")
        vol3, opp3 = context.book_volunteer(
            volunteer_sched_event=vol_context.opp_event,
            role="Waitlisted")
        vol4, opp4 = context.book_volunteer(
            volunteer_sched_event=vol_context.opp_event,
            role="Rejected")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(vol1))
        self.assertContains(response, str(vol2))
        self.assertContains(response, str(vol3))
        self.assertNotContains(response, str(vol4))
        self.assertNotContains(response, reverse(
            "approve_volunteer",
            urlconf='gbe.scheduling.urls',
            args=['approve', vol1.pk, opp1.pk]))
        self.assertContains(response, reverse(
            "approve_volunteer",
            urlconf='gbe.scheduling.urls',
            args=['approve', vol2.pk, opp2.pk]))
        self.assertContains(response, reverse(
            "approve_volunteer",
            urlconf='gbe.scheduling.urls',
            args=['approve', vol3.pk, opp3.pk]))
        self.assertContains(response, context.area.title)

    def test_post_success(self):
        login_as(self.profile, self)
        response = self.client.post(
            self.url,
            data=self.get_basic_post(),
            follow=True)
        self.assertContains(response, act_order_submit_success)
        self.assertContains(response,
                            "%s Dashboard" % self.context.sched_event.title)

    def test_post_invalid(self):
        login_as(self.profile, self)
        response = self.client.post(
            self.url,
            data=self.get_basic_post(-1),
            follow=True)
        self.assertContains(response, act_order_form_invalid)
        self.assertContains(response,
                            "%s Dashboard" % self.context.sched_event.title)

    def test_good_user_post_bad_show(self):
        login_as(self.profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.other_context.sched_event.pk+100])
        response = self.client.post(
            bad_url,
            data=self.get_basic_post(),
            follow=True)
        self.assertContains(
            response,
            "OCCURRENCE_NOT_FOUND  Occurrence id %d not found" % (
                self.other_context.sched_event.pk+100))
