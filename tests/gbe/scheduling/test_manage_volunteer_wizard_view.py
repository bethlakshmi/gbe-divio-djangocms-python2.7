from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    AvailableInterestFactory,
    GenericEventFactory,
    ProfileFactory,
    RoomFactory
)
from scheduler.models import (
    Event,
    EventContainer,
    EventLabel,
)
from tests.functions.gbe_functions import (
    assert_option_state,
    grant_privilege,
    login_as,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from gbe.models import AvailableInterest
from django.utils.formats import date_format
from django.db.models import Max
from scheduler.models import Event


class TestManageVolunteerWizard(TestCase):
    view_name = 'manage_vol'

    def setUp(self):
        AvailableInterest.objects.all().delete()
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        self.avail_interest = AvailableInterestFactory()
        self.room = RoomFactory()
        self.context = VolunteerContext()
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk])

    def get_new_opp_data(self, context):
        data = {
            'create': 'create',
            'new_opp-e_title': 'New Volunteer Opportunity',
            'new_opp-volunteer_type': self.avail_interest.pk,
            'new_opp-type': "Volunteer",
            'new_opp-max_volunteer': '1',
            'new_opp-duration': '1.0',
            'new_opp-day': self.context.window.day.pk,
            'new_opp-time': '10:00:00',
            'new_opp-location': self.room.pk}
        return data

    def get_basic_data(self, context):
        data = {
            'e_title': 'Copied Volunteer Opportunity',
            'volunteer_type': self.avail_interest.pk,
            'type': 'Volunteer',
            'max_volunteer': '1',
            'duration': '1.0',
            'day': self.context.window.day.pk,
            'time': '10:00:00',
            'location': self.room.pk}
        return data

    def get_basic_action_data(self, context, action):
        data = self.get_basic_data(context)
        data['e_title'] = 'Modify Volunteer Opportunity'
        data['opp_event_id'] = self.context.opportunity.event_id
        data['opp_sched_id'] = self.context.opp_event.pk
        data[action] = action
        return data

    def assert_volunteer_type_selector(self, response, selected_interest=None):
        if selected_interest:
            assert ('<select name="volunteer_type" id="id_volunteer_type">'
                    in response.content)
        else:
            assert ('<select name="new_opp-volunteer_type" '
                    'id="id_new_opp-volunteer_type">') in response.content
        assert '<option value="">---------</option>' in response.content
        for i in AvailableInterest.objects.all():
            if selected_interest and i == selected_interest:
                assert_option_state(
                    response,
                    i.pk,
                    i.interest,
                    True)
            elif i.visible:
                assert_option_state(
                    response,
                    i.pk,
                    i.interest,
                    False)
            else:
                assert i.interest not in response.content

    def test_no_login_gives_error(self):
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[self.context.conference.conference_slug,
                            "1"])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[self.context.conference.conference_slug,
                            "1"])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_w_interest(self):
        AvailableInterestFactory()
        AvailableInterestFactory(visible=False)
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assert_volunteer_type_selector(response)

    def test_create_opportunity(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_new_opp_data(self.context),
            follow=True)
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event).exclude(
            child_event=self.context.opp_event)
        self.assertTrue(opps.exists())
        for opp in opps:
            self.assertEqual(opp.child_event.eventitem.child().e_title,
                             'New Volunteer Opportunity')
            self.assert_volunteer_type_selector(
                response,
                opp.child_event.eventitem.child().volunteer_type)
            self.assertRedirects(
                response,
                "%s?changed_id=%d&volunteer_open=True" % (
                    reverse('edit_show',
                            urlconf='gbe.scheduling.urls',
                            args=[self.context.conference.conference_slug,
                                  self.context.sched_event.pk]),
                    opp.child_event.pk))
            self.assertEqual(EventLabel.objects.filter(
                text=opp.child_event.eventitem.child(
                    ).e_conference.conference_slug,
                event=opp.child_event).count(), 1)
            self.assertEqual(EventLabel.objects.filter(
                text="Volunteer",
                event=opp.child_event).count(), 1)

        self.assertContains(
            response,
            '<input type="text" name="e_title" value="New Volunteer ' +
            'Opportunity" required id="id_e_title" maxlength="128" />')

    def test_create_opportunity_for_staff_area(self):
        staff_context = StaffAreaContext(conference=self.context.conference)
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[staff_context.area.pk])
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_new_opp_data(self.context),
            follow=True)
        opps = Event.objects.filter(eventlabel__text=staff_context.area.slug)
        self.assertTrue(opps.exists())
        for opp in opps:
            self.assertEqual(opp.eventitem.child().e_title,
                             'New Volunteer Opportunity')
            self.assert_volunteer_type_selector(
                response,
                opp.eventitem.child().volunteer_type)
            self.assertRedirects(
                response,
                "%s?changed_id=%d&volunteer_open=True" % (
                    reverse('edit_staff',
                            urlconf='gbe.scheduling.urls',
                            args=[staff_context.area.pk]),
                    opp.pk))
            self.assertEqual(EventLabel.objects.filter(
                text=opp.eventitem.child(
                    ).e_conference.conference_slug,
                event=opp).count(), 1)
            self.assertEqual(EventLabel.objects.filter(
                text="Volunteer",
                event=opp).count(), 1)

        self.assertContains(
            response,
            '<input type="text" name="e_title" value="New Volunteer ' +
            'Opportunity" required id="id_e_title" maxlength="128" />')

    def test_create_opportunity_bad_parent(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        max_id = Event.objects.aggregate(Max('pk'))['pk__max']+1
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.conference.conference_slug, max_id])
        response = self.client.post(
            self.url,
            data=self.get_new_opp_data(self.context),
            follow=True)
        self.assertContains(
            response,
            "Occurrence id %d not found" % (max_id))

    def test_create_opportunity_bad_area(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        staff_context = StaffAreaContext(conference=self.context.conference)
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[staff_context.area.pk+100])
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_new_opp_data(self.context),
            follow=True)
        self.assertEqual(response.status_code, 404)

    def test_create_opportunity_error(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        data = self.get_new_opp_data(self.context)
        data['new_opp-max_volunteer'] = ''

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event).count()
        self.assertEqual(opps, 1)
        self.assertContains(
            response,
            '<ul class="errorlist"><li>This field is required.</li></ul>')

    def test_copy_opportunity(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        data = self.get_basic_data(self.context)
        data['duplicate'] = 'duplicate'
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        self.assertTrue(len(opps), 2)
        for opp in opps:
            self.assertContains(
                response,
                ('<input type="text" name="e_title" value="%s" ' +
                 'required id="id_e_title" maxlength="128" />') % (
                 opp.child_event.eventitem.child().e_title))
            if opp.child_event != self.context.opp_event:
                self.assertRedirects(
                    response,
                    "%s?changed_id=%d&volunteer_open=True" % (reverse(
                        'edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.context.sched_event.pk]),
                                          opp.child_event.pk))

    def test_edit_opportunity(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)

        response = self.client.post(
            self.url,
            data=self.get_basic_action_data(self.context, 'edit'),
            follow=True)
        self.assertRedirects(
            response,
            "%s?changed_id=%d&volunteer_open=True" % (
                reverse('edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.context.sched_event.pk]),
                self.context.opp_event.pk))
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        self.assertTrue(len(opps), 1)
        self.assertContains(
            response,
            '<input type="text" name="e_title" value="Modify Volunteer ' +
            'Opportunity" required id="id_e_title" maxlength="128" />')

    def test_edit_opportunity_change_room(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_basic_action_data(self.context, 'edit'),
            follow=True)
        self.assertRedirects(
            response,
            "%s?changed_id=%d&volunteer_open=True" % (
                reverse('edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.context.sched_event.pk]),
                self.context.opp_event.pk))
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        self.assertTrue(len(opps), 1)
        self.assertContains(response, self.room.name)

    def test_edit_opportunity_error(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        data = self.get_basic_action_data(self.context, 'edit')
        data['max_volunteer'] = ''

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<input type="text" name="e_title" value="Modify Volunteer ' +
            'Opportunity" required id="id_e_title" maxlength="128" />')
        self.assertContains(
            response,
            '<ul class="errorlist"><li>This field is required.</li></ul>')

    def test_delete_opportunity(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=self.get_basic_action_data(self.context, 'delete'),
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Modify Volunteer Opportunity')
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        self.assertFalse(opps.exists())

    def test_weird_action(self):
        special_context = VolunteerContext(event=GenericEventFactory())
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[special_context.conference.conference_slug,
                  special_context.sched_event.pk])
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=self.get_basic_action_data(special_context, 'inflate'),
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Modify Volunteer Opportunity')
        self.assertContains(response, "This is an unknown action.")

    def test_allocate_opportunity(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)

        # number of volunteers is missing, it's required
        data = self.get_basic_action_data(self.context, 'allocate')
        data['max_volunteer'] = ''
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Modify Volunteer Opportunity')
        opps = EventContainer.objects.filter(
            parent_event=self.context.sched_event)
        self.assertTrue(opps.exists())
        self.assertContains(response, "Volunteer Allocation")
