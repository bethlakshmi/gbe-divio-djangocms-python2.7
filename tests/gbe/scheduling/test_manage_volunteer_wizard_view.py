from django.urls import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
    RoomFactory
)
from scheduler.models import (
    Event,
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
from django.utils.formats import date_format
from django.db.models import Max
from scheduler.models import Event


class TestManageVolunteerWizard(TestCase):
    view_name = 'manage_vol'

    @classmethod
    def setUpTestData(cls):
        cls.user = ProfileFactory.create().user_object
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Volunteer Coordinator')
        cls.room = RoomFactory()
        # because there was a bug around duplicate room names
        RoomFactory(name=cls.room.name)
        cls.context = VolunteerContext()
        cls.room.conferences.add(cls.context.conference)
        cls.url = reverse(
            cls.view_name,
            urlconf="gbe.scheduling.urls",
            args=[cls.context.conference.conference_slug,
                  cls.context.sched_event.pk])

    def setUp(self):
        self.client = Client()

    def get_new_opp_data(self, context):
        data = {
            'create': 'create',
            'new_opp-title': 'New Volunteer Opportunity',
            'new_opp-event_style': "Volunteer",
            'new_opp-max_volunteer': '1',
            'new_opp-approval': True,
            'new_opp-duration': '1.0',
            'new_opp-day': self.context.conf_day.pk,
            'new_opp-time': '10:00:00',
            'new_opp-location': self.room.pk}
        return data

    def get_basic_data(self, context):
        data = {
            'approval': True,
            'title': 'Copied Volunteer Opportunity',
            'event_style': 'Volunteer',
            'max_volunteer': '1',
            'duration': '1.0',
            'day': self.context.conf_day.pk,
            'time': '10:00:00',
            'location': self.room.pk}
        return data

    def get_basic_action_data(self, context, action):
        data = self.get_basic_data(context)
        data['title'] = 'Modify Volunteer Opportunity'
        data['opp_sched_id'] = self.context.opp_event.pk
        data[action] = action
        return data

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

    def test_good_user_get(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<input type="checkbox" name="new_opp-approval" ' +
            'id="id_new_opp-approval" />',
            html=True)

    def test_create_opportunity(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_new_opp_data(self.context),
            follow=True)
        opps = Event.objects.filter(
            parent=self.context.sched_event).exclude(
            pk=self.context.opp_event.pk)
        self.assertTrue(opps.exists())
        for opp in opps:
            self.assertEqual(opp.title,
                             'New Volunteer Opportunity')
            self.assertTrue(opp.approval_needed)
            self.assertRedirects(
                response,
                "%s?changed_id=%d&volunteer_open=True" % (
                    reverse('edit_show',
                            urlconf='gbe.scheduling.urls',
                            args=[self.context.conference.conference_slug,
                                  self.context.sched_event.pk]),
                    opp.pk))
            self.assertEqual(EventLabel.objects.filter(
                text=self.context.conference.conference_slug,
                event=opp).count(), 1)
            self.assertEqual(EventLabel.objects.filter(
                text="Volunteer",
                event=opp).count(), 1)

        self.assertContains(
            response,
            '<input type="text" name="title" value="New Volunteer ' +
            'Opportunity" maxlength="128" required id="id_title" />',
            html=True)
        self.assertContains(
            response,
            '<input type="checkbox" name="approval" ' +
            'id="id_approval" checked />',
            html=True)

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
            self.assertEqual(opp.title,
                             'New Volunteer Opportunity')
            self.assertTrue(opp.approval_needed)

            self.assertRedirects(
                response,
                "%s?changed_id=%d&volunteer_open=True" % (
                    reverse('edit_staff',
                            urlconf='gbe.scheduling.urls',
                            args=[staff_context.area.pk]),
                    opp.pk))
            self.assertEqual(EventLabel.objects.filter(
                text=self.context.conference.conference_slug,
                event=opp).count(), 1)
            self.assertEqual(EventLabel.objects.filter(
                text="Volunteer",
                event=opp).count(), 1)
        self.assertContains(
            response,
            '<input type="text" name="title" value="New Volunteer ' +
            'Opportunity" maxlength="128" required id="id_title" />',
            html=True)
        self.assertContains(
            response,
            '<input type="checkbox" name="approval" ' +
            'id="id_approval" checked />',
            html=True)

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
        opps = Event.objects.filter(
            parent=self.context.sched_event).count()
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
        opps = Event.objects.filter(parent=self.context.sched_event)
        self.assertTrue(len(opps), 2)
        for opp in opps:
            checked = ""
            if opp.approval_needed:
                checked = "checked "
            self.assertContains(
                response,
                '<input type="checkbox" name="approval" ' +
                'id="id_approval" %s/>' % checked,
                html=True)
            self.assertContains(
                response,
                ('<input type="text" name="title" value="%s" ' +
                 'maxlength="128" required id="id_title" />') % (
                 opp.title),
                html=True)
            if opp != self.context.opp_event:
                self.assertRedirects(
                    response,
                    "%s?changed_id=%d&volunteer_open=True" % (reverse(
                        'edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.context.sched_event.pk]),
                                          opp.pk))

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
        opps = Event.objects.filter(
            parent=self.context.sched_event)
        self.assertTrue(len(opps), 1)
        self.assertTrue(opps[0].approval_needed)
        self.assertContains(
            response,
            '<input type="text" name="title" value="Modify Volunteer ' +
            'Opportunity" maxlength="128" required id="id_title" />',
            html=True)

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
        opps = Event.objects.filter(parent=self.context.sched_event)
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
            '<input type="text" name="title" value="Modify Volunteer ' +
            'Opportunity" maxlength="128" required id="id_title" />',
            html=True)
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
        self.assertFalse(
            Event.objects.filter(parent=self.context.sched_event).exists())

    def test_weird_action(self):
        special_context = VolunteerContext(event_style="Special")
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
        self.assertTrue(
            Event.objects.filter(parent=self.context.sched_event).exists())
        self.assertContains(response, "Volunteer Allocation")
