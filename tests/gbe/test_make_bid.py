from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ConferenceFactory,
    EmailTemplateSenderFactory,
    ProfileFactory,
    ProfilePreferencesFactory,
    UserFactory,
    UserMessageFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_right_mail_right_addresses,
    grant_privilege,
    login_as,
)
from gbe.models import (
    Conference,
)
from post_office.models import EmailTemplate
from gbe_utils.text import no_profile_msg


class TestMakeBid(TestCase):
    '''Tests for the centralized make bid view'''
    view_name = 'class_create'

    @classmethod
    def setUpTestData(cls):
        Conference.objects.all().delete()
        cls.performer = BioFactory()
        cls.conference = ConferenceFactory(accepting_bids=True)

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
                }
        if submit:
            data['submit'] = 1
        return data

    def post_bid(self, submit=True):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.contact, self)
        data = self.get_form(submit=submit)
        response = self.client.post(url, data=data, follow=True)
        return response, data

    def test_create_no_login(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            "%s?next=%s" % (
                reverse('register', urlconf='gbe.urls'),
                url))

    def test_get_no_profile(self):
        '''when user has no profile, should bounce out to /profile'''
        url = reverse(self.view_name, urlconf='gbe.urls')
        user = UserFactory()
        login_as(user, self)
        response = self.client.get(url, )
        self.assertRedirects(
            response,
            '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'), url))

    def test_edit_bad_bid_id(self):
        '''Should get 404 if no valid class ID'''
        url = reverse('class_edit',
                      args=[0],
                      urlconf='gbe.urls')
        login_as(BioFactory().contact, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_post_no_profile(self):
        '''when user has no profile, should bounce out to /profile'''
        url = reverse("act_create", urlconf='gbe.urls')
        user = UserFactory()
        login_as(user, self)
        # this is class data, not act data, but won't get far enough to care
        data = self.get_form()
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(
            response,
            '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'), url))

    def test_create_bad_profile(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        cptn_tinypants = ProfileFactory(display_name="", phone="")
        ProfilePreferencesFactory(profile=cptn_tinypants)
        login_as(cptn_tinypants.user_object, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            "%s?next=%s" % (
                reverse('profile_update', urlconf='gbe.urls'),
                url))
        assert_alert_exists(
            response, 'warning', 'Warning', no_profile_msg)

    def test_bid_no_conference(self):
        '''when there is no conference accepting bids, should throw 404'''
        Conference.objects.all().delete()
        self.conference = ConferenceFactory(accepting_bids=False)
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.contact, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '/')

    def test_get_new_bid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.conference.conference_name)
        self.assertContains(response, 'We will do our best to accommodate')

    def test_class_posting_sends_mails(self):
        # 1 mail to reviewers
        # 1 mail to submitter as confirmation
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Class Reviewers')
        EmailTemplate.objects.all().delete()
        subject_format = "bidder: %s, bid: %s"
        EmailTemplateSenderFactory(
            from_email="class@notify.com",
            from_name="Class Committee",
            template__name='class submission notification',
            template__subject="bidder: %s, bid: %s" % (
                "{{ bidder }}",
                "{{ bid.b_title }}")
        )
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.contact, self)
        data = self.get_form()
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        assert_right_mail_right_addresses(
            0,
            2,
            "bidder: %s, bid: %s" % (
                str(self.performer.contact),
                data['theclass-b_title']),
            [privileged_profile.contact_email],
            from_email="class@notify.com",
            from_name="Class Committee")
        assert_right_mail_right_addresses(
            1,
            2,
            'Your class proposal has changed status to Submitted',
            [self.performer.contact.contact_email])

    def test_class_submit_has_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        msg = UserMessageFactory(
            view='MakeClassView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_bid(submit=True)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_class_draft_has_message(self):
        '''class_bid, not submitting and no other problems,
        should redirect to home'''
        msg = UserMessageFactory(
            view='MakeClassView',
            code='DRAFT_SUCCESS')
        response, data = self.post_bid(submit=False)
        self.assertEqual(200, response.status_code)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
