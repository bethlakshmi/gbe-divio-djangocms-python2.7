from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
    PersonaFactory,
    UserMessageFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    location,
)
from gbetext import (
    default_class_submit_msg,
    default_class_draft_msg
)
from gbe.models import (
    Conference,
    UserMessage
)


class TestEditClass(TestCase):
    '''Tests for edit_class view'''
    view_name = 'class_edit'

    def setUp(self):
        Conference.objects.all().delete()
        UserMessage.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.teacher = PersonaFactory()

    def get_form(self, submit=True, invalid=False):
        data = {"theclass-teacher": self.teacher.pk,
                "theclass-b_title": 'A class',
                "theclass-b_description": 'a description',
                "theclass-length_minutes": 60,
                'theclass-maximum_enrollment': 20,
                'theclass-fee': 0,
                'theclass-schedule_constraints': ['0'],
                }
        if submit:
            data['submit'] = 1
        if invalid:
            del(data['theclass-b_title'])
        return data

    def post_class_edit_submit(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        data = self.get_form()
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def post_class_edit_draft(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        data = self.get_form(submit=False)
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def test_edit_class_no_class(self):
        '''Should get 404 if no valid class ID'''
        url = reverse(self.view_name,
                      args=[0],
                      urlconf='gbe.urls')
        login_as(PersonaFactory().performer_profile, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_edit_class_profile_is_not_contact(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(PersonaFactory().performer_profile, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_class_edit_post_form_not_valid(self):
        '''class_edit, if form not valid, should return to ActEditForm'''
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
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

    def test_edit_bid_not_post(self):
        '''edit_bid, not post, should take us to edit process'''
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Submit a Class')

    def test_edit_bid_verify_info_popup_text(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'We will do our best to accommodate')

    def test_edit_bid_verify_constraints(self):
        klass = ClassFactory(schedule_constraints="[u'0']",
                             avoided_constraints="[u'1', u'2']")
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        login_as(klass.teacher.performer_profile, self)
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
        # should test some change to class

    def test_class_submit_make_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_class_edit_submit()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_class_submit_msg)

    def test_class_draft_make_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        response, data = self.post_class_edit_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', default_class_draft_msg)

    def test_class_submit_has_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        msg = UserMessageFactory(
            view='MakeClassView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_class_edit_submit()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_class_draft_has_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        msg = UserMessageFactory(
            view='MakeClassView',
            code='DRAFT_SUCCESS')
        response, data = self.post_class_edit_draft()
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
