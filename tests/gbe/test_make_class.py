from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ClassFactory,
    ConferenceFactory,
    ProfileFactory,
    UserMessageFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
)
from gbetext import (
    default_class_submit_msg,
    default_class_draft_msg
)
from gbe.models import (
    Class,
    Conference,
    Profile,
    UserMessage,
)


class TestMakeClass(TestCase):
    '''Parent for class testing'''

    @classmethod
    def setUpTestData(cls):
        Conference.objects.all().delete()
        UserMessage.objects.all().delete()
        cls.performer = BioFactory()

    def setUp(self):
        self.client = Client()

    def get_form(self, submit=True, invalid=False):
        data = {"theclass-teacher_bio": self.performer.pk,
                'theclass-phone': '111-222-3333',
                'theclass-first_name': 'Jane',
                'theclass-last_name': 'Smith',
                "theclass-b_title": 'A class',
                "theclass-b_description": 'a description',
                "theclass-length_minutes": 60,
                'theclass-maximum_enrollment': 20,
                'theclass-fee': 0,
                'theclass-schedule_constraints': ['0'],
                'theclass-space_needs': "",
                }
        if submit:
            data['submit'] = 1
        if invalid:
            del(data['theclass-b_title'])
        return data

    def check_subway_state(self, response, active_state="Apply"):
        self.assertContains(
            response,
            '<li class="progressbar_active">%s</li>' % active_state,
            html=True)
        self.assertNotContains(
                response,
                '<li class="progressbar_upcoming">Payment</li>',
                html=True)


class TestCreateClass(TestMakeClass):
    '''Tests for create_class view'''
    view_name = 'class_create'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.conference = ConferenceFactory(accepting_bids=True)

    def post_bid(self, submit=True):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.contact, self)
        data = self.get_form(submit=submit)
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def test_bid_class_no_personae(self):
        '''class_bid, when profile has no personae,
        should redirect to persona-add'''
        profile = ProfileFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(profile, self)
        response = self.client.get(
            url,
            follow=True)
        self.assertRedirects(
            response,
            reverse("persona-add", urlconf='gbe.urls', args=[0]) +
            "?next=/class/create")
        title = '<h3 class="gbe-title">Tell Us About Your Bio</h3>'
        self.assertContains(response, title, html=True)
        self.assertNotContains(response, "Create Troupe")
        self.check_subway_state(response, active_state="Create Bio")

    def test_class_bid_post_with_submit_incomplete(self):
        '''class_bid, submit, incomplete form'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')

        data = self.get_form(submit=True, invalid=True)
        user = self.performer.contact.user_object
        login_as(user, self)
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        expected_string = "This field is required"
        self.assertContains(response, expected_string)
        self.check_subway_state(response)

    def test_class_bid_post_invalid_form_no_submit(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        other_performer = BioFactory()
        other_profile = other_performer.contact
        login_as(self.performer.contact, self)
        data = self.get_form(submit=False, invalid=True)
        data['theclass-teacher_bio'] = other_performer.pk
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Submit a Class')
        self.assertContains(
            response,
            'Select a valid choice. That choice is not one of the available' +
            ' choices.')
        self.check_subway_state(response)

    def test_class_bid_verify_avoided_constraints(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'I Would Prefer to Avoid')
        self.check_subway_state(response)

    def test_class_submit_make_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_bid(submit=True)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_class_submit_msg)
        self.assertContains(response, data['theclass-b_title'])

    def test_class_submit_conflict_times(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.contact, self)
        data = self.get_form(submit=True)
        data['theclass-avoided_constraints'] = ['0']
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Available times conflict with unavailable times.  " +
            "Conflicts are: Friday Afternoon")
        self.check_subway_state(response)

    def test_class_draft_make_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_bid(submit=False)
        profile = Profile.objects.get(pk=self.performer.contact.pk)
        self.assertEqual(profile.phone, '111-222-3333')
        self.assertEqual(profile.user_object.first_name, 'Jane')
        self.assertEqual(profile.user_object.last_name, 'Smith')
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_class_draft_msg)
        self.assertContains(response, 'Welcome to GBE')
        self.assertContains(response, data['theclass-b_title'])


class TestEditClass(TestMakeClass):
    '''Tests for edit_class view'''
    view_name = 'class_edit'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.teacher = cls.performer

    def post_class_edit_submit(self):
        klass = ClassFactory(teacher_bio=self.teacher)
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.contact, self)
        data = self.get_form()
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def post_class_edit_draft(self):
        klass = ClassFactory(teacher_bio=self.teacher)
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher_bio.contact, self)
        data = self.get_form(submit=False)
        data['theclass-b_title'] = '"extra quotes"'
        data["theclass-teacher_bio"] = klass.teacher_bio.pk
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def test_edit_class_profile_is_not_contact(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(BioFactory().contact, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_class_edit_post_form_not_valid(self):
        '''class_edit, if form not valid, should return to ActEditForm'''
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher_bio.contact, self)
        data = self.get_form(invalid=True)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Submit a Class')

    def test_edit_bid_post_no_submit(self):
        '''act_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_class_edit_draft()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        self.assertNotContains(response, data['theclass-b_title'])
        self.assertContains(response, data['theclass-b_title'].strip('\"\''))

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        klass = ClassFactory()
        klass.teacher_bio.contact.phone = "555-666-7777"
        klass.teacher_bio.contact.save()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher_bio.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Submit a Class')
        self.assertContains(response, klass.b_title)
        self.assertContains(response, "555-666-7777")
        self.check_subway_state(response)

    def test_edit_bid_verify_info_popup_text(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher_bio.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'We will do our best to accommodate')
        self.check_subway_state(response)

    def test_edit_bid_verify_constraints(self):
        klass = ClassFactory(schedule_constraints="[u'0']",
                             avoided_constraints="[u'1', u'2']")
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher_bio.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        constraint_selected = '<input type="checkbox" name="theclass-%s" ' + \
            'value="%d" id="id_theclass-%s_%d" checked />'
        self.assertContains(
            response,
            constraint_selected % (
                "schedule_constraints",
                0,
                "schedule_constraints",
                0),
            html=True)
        self.assertContains(
            response,
            constraint_selected % (
                "avoided_constraints",
                1,
                "avoided_constraints",
                1),
            html=True)
        self.assertContains(
            response,
            constraint_selected % (
                "avoided_constraints",
                2,
                "avoided_constraints",
                2),
            html=True)

    def test_edit_class_post_with_submit(self):
        response, data = self.post_class_edit_submit()
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        profile = Profile.objects.get(pk=self.teacher.contact.pk)
        self.assertEqual(profile.phone, '111-222-3333')
