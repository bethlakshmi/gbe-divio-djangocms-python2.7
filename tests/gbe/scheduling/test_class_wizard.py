from django.test import TestCase
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ClassFactory,
    ClassLabelFactory,
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
    RoomFactory,
)
from scheduler.models import Event
from gbe.models import Class
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    grant_privilege,
    login_as,
)
from settings import GBE_DATE_FORMAT
from tests.gbe.scheduling.test_scheduling import TestScheduling


class TestClassWizard(TestScheduling):
    '''Tests for the 2nd and 3rd stage in the class wizard view'''
    view_name = 'create_class_wizard'

    @classmethod
    def setUpTestData(cls):
        cls.room = RoomFactory()
        # because there was a bug around duplicate room names
        RoomFactory(name=cls.room.name)
        cls.teacher = BioFactory()
        cls.current_conference = ConferenceFactory()
        cls.day = ConferenceDayFactory(conference=cls.current_conference)
        cls.room.conferences.add(cls.current_conference)
        cls.test_class = ClassFactory(b_conference=cls.current_conference,
                                      accepted=3,
                                      teacher_bio=cls.teacher,
                                      submitted=True,
                                      difficulty="Medium")
        cls.orig_label = ClassLabelFactory()
        cls.test_class.labels.add(cls.orig_label)
        cls.url = reverse(
            cls.view_name,
            args=[cls.current_conference.conference_slug],
            urlconf='gbe.scheduling.urls')
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Scheduling Mavens')

    def get_data(self):
        data = {
            'accepted_class': self.test_class.pk,
            'pick_class': 'Next'
        }
        return data

    def edit_class(self):
        data = {
            'id': self.test_class.pk,
            'accepted': 3,
            'submitted': True,
            'type': 'Panel',
            'b_title': "Test Class Wizard #%d" % self.test_class.pk,
            'b_description': 'Description',
            'maximum_enrollment': 10,
            'fee': 0,
            'difficulty': "Hard",
            'max_volunteer': 0,
            'day': self.day.pk,
            'time': '11:00:00',
            'duration': 2.5,
            'location': self.room.pk,
            'alloc_0-role': 'Teacher',
            'alloc_0-worker': self.teacher.pk,
            'alloc_1-role': 'Volunteer',
            'alloc_1-worker': "",
            'set_class': 'Finish',
        }
        return data

    def test_create_event_unauthorized_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_authorized_user_can_access(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assert_event_was_picked_in_wizard(response, "conference")
        self.assertContains(response, str(self.test_class.b_title))
        self.assertContains(response, str(self.test_class.teacher))

    def test_authorized_user_single_conference(self):
        other_class = ClassFactory(accepted=3,
                                   submitted=True)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, str(other_class.b_title))
        self.assertNotContains(response, str(other_class.teacher))

    def test_authorized_user_third_form_get(self):
        # this is how the class coordinator can fast schedule from review
        login_as(self.privileged_user, self)
        response = self.client.get("%s?accepted_class=%d" % (
            self.url,
            self.test_class.pk))
        self.assertContains(
            response,
            ('<input type="radio" name="accepted_class" value="%d" ' +
             'id="id_accepted_class_1" checked />') % self.test_class.pk,
            html=True)
        self.assertContains(
            response,
            'value="%s"' %
            self.test_class.b_title)
        self.assertContains(
            response,
            'type="number" name="duration" value="1.0"')
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (
                self.day.pk,
                self.day.day.strftime(GBE_DATE_FORMAT)),
            html=True)
        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                self.test_class.teacher.pk,
                str(self.test_class.teacher)),
            html=True)
        self.assertContains(
            response,
            ('<input type="radio" name="difficulty" value="Medium" ' +
             'id="id_difficulty_1" checked/>'),
            html=True)
        assert_option_state(response,
                            self.orig_label.pk,
                            self.orig_label.text,
                            True)

    def test_auth_user_can_pick_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            ('<input type="radio" name="accepted_class" value="%d" ' +
             'id="id_accepted_class_1" checked />') % self.test_class.pk,
            html=True)

    def test_invalid_form(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        data['accepted_class'] = "boo"
        response = self.client.post(
            self.url,
            data=data)
        self.assertContains(
            response,
            'That choice is not one of the available choices.')

    def test_auth_user_pick_new_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        data['accepted_class'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            '<input type="radio" name="accepted_class" value="" ' +
            'id="id_accepted_class_0" checked />',
            html=True)
        self.assertContains(
            response,
            'Make New Class')
        self.assertContains(
            response,
            'name="duration" value="1"')
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (
                self.day.pk,
                self.day.day.strftime(GBE_DATE_FORMAT)),
            html=True)
        self.assert_role_choice(response, 'Teacher')

    def test_auth_user_load_class(self):
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            'value="%s"' %
            self.test_class.b_title)
        self.assertContains(
            response,
            'type="number" name="duration" value="1.0"')
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (
                self.day.pk,
                self.day.day.strftime(GBE_DATE_FORMAT)),
            html=True)
        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                self.test_class.teacher.pk,
                str(self.test_class.teacher)),
            html=True)

    def test_auth_user_load_panel(self):
        panel = ClassFactory(b_conference=self.current_conference,
                             type="Panel",
                             accepted=3,
                             teacher_bio=self.teacher,
                             submitted=True)
        login_as(self.privileged_user, self)
        data = self.get_data()
        data['accepted_class'] = panel.pk
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            'value="%s"' %
            panel.b_title)
        self.assertContains(response, "Panelist")
        self.assertContains(response, "Moderator")
        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                panel.teacher.pk,
                str(panel.teacher)),
            html=True)

    def test_auth_user_edit_class(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        label = ClassLabelFactory()
        data['labels'] = [label.pk]
        data['slug'] = "classsluggy"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        occurrence = Event.objects.filter(connected_id=self.test_class.pk)
        updated_class = Class.objects.get(pk=self.test_class.pk)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence[0].pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['b_title'],
                self.day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-success">\n       ' +
            '<td>%s</td>' % data['b_title'])
        self.assertEqual(updated_class.difficulty, data['difficulty'])
        self.assertTrue(updated_class.labels.filter(pk=label.pk).exists())
        self.assertEqual(occurrence[0].slug, data['slug'])

    def test_auth_user_create_class(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        del data['id']
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        new_class = Class.objects.get(b_title=data['b_title'])
        self.assertEqual(new_class.teacher, self.teacher)
        occurrence = Event.objects.get(connected_id=new_class.pk)
        self.assertRedirects(
            response,
            "%s?%s-day=%d&filter=Filter&new=[%d]" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[self.current_conference.conference_slug]),
                self.current_conference.conference_slug,
                self.day.pk,
                occurrence.pk))
        assert_alert_exists(
            response,
            'success',
            'Success',
            'Occurrence has been updated.<br>%s, Start Time: %s 11:00 AM' % (
                data['b_title'],
                self.day.day.strftime(GBE_DATE_FORMAT))
            )
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-success">\n       ' +
            '<td>%s</td>' % data['b_title'])

    def test_auth_user_create_class_no_teacher(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['id'] = ""
        data['alloc_0-worker'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            "You must select at least one person to run this class."
            )

    def test_auth_user_bad_user_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['alloc_0-role'] = "bad role"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "bad role is not one of the available choices.")

    def test_auth_user_bad_schedule_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['location'] = ""
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(response, "This field is required.")

    def test_auth_user_bad_class_booking_assign(self):
        login_as(self.privileged_user, self)
        data = self.edit_class()
        data['type'] = "bad type"
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertContains(
            response,
            "bad type is not one of the available choices.")

    def test_get_class_recommendations(self):
        self.test_class.schedule_constraints = "[u'1']"
        self.test_class.avoided_constraints = "[u'2']"
        self.test_class.space_needs = "2"
        self.test_class.type = "Panel"
        self.test_class.save()
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assert_good_sched_event_form_wizard(response, self.test_class)

    def test_get_empty_schedule_info(self):
        self.test_class.schedule_constraints = ""
        self.test_class.avoided_constraints = ""
        self.test_class.space_needs = ""
        self.test_class.type = ""
        self.test_class.save()
        login_as(self.privileged_user, self)
        data = self.get_data()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assert_good_sched_event_form_wizard(response, self.test_class)
