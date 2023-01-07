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
    ResourceAllocation,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.contexts import (
    ActTechInfoContext,
    ShowContext,
)
from django.utils.formats import date_format
from datetime import timedelta


class TestEditShowWizard(TestCase):
    view_name = 'manage_show_opp'
    title_field = '<input type="text" name="title" value="%s" ' + \
        'maxlength="128" required id="id_title" />'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.user = ProfileFactory.create().user_object
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Scheduling Mavens')
        grant_privilege(cls.privileged_user, 'Volunteer Coordinator')
        cls.room = RoomFactory()
        cls.context = ShowContext()
        cls.room.conferences.add(cls.context.conference)
        cls.url = reverse(
            cls.view_name,
            urlconf="gbe.scheduling.urls",
            args=[cls.context.conference.conference_slug,
                  cls.context.sched_event.pk])

    def get_new_slot_data(self, context):
        data = {
            'create_slot': 'create_slot',
            'new_slot-title': 'New Rehearsal Slot',
            'new_slot-event_style': "Rehearsal Slot",
            'new_slot-max_volunteer': '1',
            'new_slot-duration': '1.0',
            'new_slot-day': self.context.days[0].pk,
            'new_slot-time': '10:00:00',
            'new_slot-location': self.room.pk}
        return data

    def get_basic_data(self, context):
        data = {
            'title': 'Copied Rehearsal Slot',
            'event_style': 'Rehearsal Slot',
            'max_volunteer': '1',
            'duration': '1.0',
            'day': self.context.days[0].pk,
            'time': '10:00:00',
            'location': self.room.pk}
        return data

    def get_basic_action_data(self, context, action):
        data = self.get_basic_data(context)
        slot = self.context.make_rehearsal()
        data['title'] = 'Modify Rehearsal Slot'
        data['opp_sched_id'] = slot.pk
        data[action] = action
        return data, slot

    def test_good_user_get(self):
        self.url = reverse(
            "edit_show",
            urlconf="gbe.scheduling.urls",
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk])
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, "Edit Show Details")
        self.assertContains(response, "Manage Volunteer Opportunities")
        self.assertContains(response, "Manage Rehearsal Slots")
        self.assertContains(
            response,
            'class="panel-collapse collapse show"',
            3)
        print(response.content)
        self.assertContains(
            response,
            '<input type="hidden" name="new_opp-event_style" value="Volunteer"'
            ' id="id_new_opp-event_style">',
            html=True)

    def test_good_user_get_rehearsal_w_acts(self):
        act_techinfo_context = ActTechInfoContext(
            sched_event=self.context.sched_event,
            schedule_rehearsal=True)
        act_techinfo_context.rehearsal.length = timedelta(hours=7, minutes=30)
        act_techinfo_context.rehearsal.save()
        self.url = reverse(
            "edit_show",
            urlconf="gbe.scheduling.urls",
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk])
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<input type="number" name="current_acts" value="1" ' +
            'readonly="readonly" id="id_current_acts" />',
            html=True)
        self.assertContains(
            response,
            '<input type="number" name="duration" value="7.5" min="0.5" ' +
            'max="12" step="any" required id="id_duration">',
            html=True)

    def test_good_user_get_empty_room_rehearsal(self):
        not_this_room = RoomFactory()
        slot = self.context.make_rehearsal(room=False)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                self.context.room.pk,
                str(self.context.room)),
            4)
        self.assertNotContains(response, str(not_this_room))
        slot.delete()

    def test_good_user_get_bad_occurrence_id(self):
        login_as(self.privileged_user, self)
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk+1000],
            urlconf='gbe.scheduling.urls')
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            reverse('manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.context.conference.conference_slug]))
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+1000))

    def test_edit_event_keep_performers(self):
        self.url = reverse(
            'edit_show',
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        login_as(self.privileged_user, self)
        data = {
            'title': "Test Show Edit",
            'description': 'Description',
            'max_volunteer': 0,
            'day': self.context.days[0].pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'alloc_0-role': 'Producer',
            'edit_event': 'Save and Continue'
        }
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?volunteer_open=True" % self.url)
        self.assertTrue(ResourceAllocation.objects.filter(
            event=self.context.sched_event,
            resource__worker___item=self.context.performer).count() == 1)

    def test_create_slot(self):
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_new_slot_data(self.context),
            follow=True)
        self.assertContains(
            response,
            '<div id="collapse3" class="panel-collapse collapse show">')
        slots = Event.objects.filter(
            parent=self.context.sched_event)
        self.assertTrue(slots.exists())
        for slot in slots:
            self.assertEqual(slot.title,
                             'New Rehearsal Slot')
            self.assertRedirects(
                response,
                "%s?changed_id=%d&rehearsal_open=True" % (
                    reverse('edit_show',
                            urlconf='gbe.scheduling.urls',
                            args=[self.context.conference.conference_slug,
                                  self.context.sched_event.pk]),
                    slot.pk))
            self.assertEqual(EventLabel.objects.filter(
                text=self.context.conference.conference_slug,
                event=slot).count(), 1)
            self.assertEqual(EventLabel.objects.filter(
                event=slot).count(), 1)

        self.assertContains(
            response,
            self.title_field % "New Rehearsal Slot",
            html=True)

    def test_create_slot_error(self):
        login_as(self.privileged_profile, self)
        data = self.get_new_slot_data(self.context)
        data['new_slot-max_volunteer'] = ''

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<div id="collapse3" class="panel-collapse collapse show">')
        self.assertFalse(
            Event.objects.filter(parent=self.context.sched_event).exists())
        self.assertContains(
            response,
            '<ul class="errorlist"><li>This field is required.</li></ul>')

    def test_copy_opportunity(self):
        login_as(self.privileged_profile, self)
        data = self.get_basic_data(self.context)
        data['duplicate_slot'] = 'duplicate_slot'
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            '<div id="collapse3" class="panel-collapse collapse show">')
        slots = Event.objects.filter(parent=self.context.sched_event)
        self.assertTrue(len(slots), 1)
        for slot in slots:
            self.assertContains(
                response,
                self.title_field % (slot.title),
                html=True)
            self.assertRedirects(
                response,
                "%s?changed_id=%d&rehearsal_open=True" % (
                    reverse(
                        'edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.context.sched_event.pk]),
                    slot.pk))

    def test_edit_slot(self):
        login_as(self.privileged_profile, self)
        data, slot = self.get_basic_action_data(self.context, 'edit_slot')
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?changed_id=%d&rehearsal_open=True" % (
                reverse('edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.context.conference.conference_slug,
                              self.context.sched_event.pk]),
                slot.pk))
        slots = Event.objects.filter(parent=self.context.sched_event)
        self.assertTrue(len(slots), 1)
        self.assertContains(
            response,
            self.title_field % "Modify Rehearsal Slot",
            html=True)
        self.assertContains(response, self.room.name)
        slot.delete()

    def test_edit_error(self):
        login_as(self.privileged_profile, self)
        data, slot = self.get_basic_action_data(self.context, 'edit_slot')
        data['max_volunteer'] = ''

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.title_field % "Modify Rehearsal Slot",
            html=True)
        self.assertContains(
            response,
            '<ul class="errorlist"><li>This field is required.</li></ul>')
        slot.delete()

    def test_delete_slot(self):
        login_as(self.privileged_profile, self)
        data, slot = self.get_basic_action_data(self.context, 'delete_slot')

        # number of volunteers is missing, it's required
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Modify Rehearsal Slot')
        self.assertFalse(Event.objects.filter(
            parent=self.context.sched_event).exists())
        slot.delete()
