from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ClassLabelFactory,
    ConferenceDayFactory,
    ProfileFactory,
)
from gbe.models import Class
from scheduler.models import Event
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
)
from settings import GBE_DATE_FORMAT
from tests.contexts import (
    ClassContext,
    VolunteerContext,
)
from datetime import timedelta
from tests.gbe.scheduling.test_scheduling import TestScheduling


class TestEditClassView(TestScheduling):
    '''This view edits classes that were made through the wizard'''
    view_name = 'edit_class'

    def setUp(self):
        self.context = ClassContext()
        self.label = ClassLabelFactory()
        self.context.sched_event.slug = "origslug"
        self.context.sched_event.save()
        self.extra_day = ConferenceDayFactory(
            conference=self.context.conference,
            day=self.context.days[0].day + timedelta(days=1))
        self.url = reverse(
            self.view_name,
            args=[self.context.conference.conference_slug,
                  self.context.sched_event.pk],
            urlconf='gbe.scheduling.urls')
        self.client = Client()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')

    def edit_event(self):
        data = {
            'type': 'Lecture',
            'b_title': "Test Class Wizard",
            'slug': "EditSlug",
            'b_description': 'Description',
            'max_volunteer': 0,
            'day': self.extra_day.pk,
            'time': '11:00:00',
            'duration': 2.25,
            'location': self.context.room.pk,
            'set_event': 'Any value',
            'alloc_0-role': 'Staff Lead',
            'difficulty': "Hard",
            'labels': [self.label.pk],
            'id': self.context.bid.pk,
            'accepted': 3,
            'submitted': True,
        }
        return data

    def test_edit_class(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, "Edit Class")
        self.assertContains(response, self.context.sched_event.title)
        self.assertContains(response, "Booking Information")
        self.assertContains(response, self.context.sched_event.slug)

    def test_edit_not_class(self):
        context = VolunteerContext()
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.view_name,
            args=[context.conference.conference_slug,
                  context.opp_event.pk],
            urlconf='gbe.scheduling.urls'), follow=True)
        self.assertRedirects(response, reverse(
            "edit_volunteer",
            args=[context.conference.conference_slug,
                  context.opp_event.pk],
            urlconf='gbe.scheduling.urls'))

    def test_edit_bad_class(self):
        context = ClassContext()
        context.sched_event.connected_id = None
        context.sched_event.save()
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.view_name,
            args=[context.conference.conference_slug,
                  context.sched_event.pk],
            urlconf='gbe.scheduling.urls'))
        self.assertEqual(404, response.status_code)

    def test_edit_class_w_teacher_and_continue(self):
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        login_as(self.privileged_user, self)
        new_teacher = BioFactory()
        data = self.edit_event()
        data['alloc_0-role'] = 'Teacher'
        data['alloc_1-role'] = 'Teacher'
        data['alloc_2-role'] = 'Teacher'
        data['alloc_3-role'] = 'Teacher'
        data['alloc_0-worker'] = new_teacher.pk
        data['alloc_1-worker'] = ''
        data['alloc_2-worker'] = ''
        data['alloc_3-worker'] = ''
        data['edit_event'] = "Save and Continue"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_class = Class.objects.get(pk=self.context.bid.pk)
        new_event = Event.objects.get(pk=self.context.sched_event.pk)
        print(response.content)
        self.assertRedirects(
            response,
            "%s?volunteer_open=True" % self.url)
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['b_title'],
                self.extra_day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(response, data['b_title'])
        self.assertContains(response, data['b_description'])
        self.assertContains(response, data['slug'])

        assert_option_state(response,
                            self.extra_day.pk,
                            self.extra_day.day.strftime(GBE_DATE_FORMAT),
                            True)
        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                new_teacher.pk,
                new_teacher.name))
        self.assertEqual(new_class.difficulty, data['difficulty']),
        self.assertTrue(new_class.labels.filter(pk=self.label.pk).exists())
        self.assertEqual(new_event.slug, data['slug']),
