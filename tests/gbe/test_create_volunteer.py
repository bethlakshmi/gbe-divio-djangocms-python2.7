from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    AvailableInterestFactory,
    ConferenceFactory,
    ConferenceDayFactory,
    ProfileFactory,
    ProfilePreferencesFactory,
    UserMessageFactory,
    VolunteerFactory,
    VolunteerWindowFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_hidden_value,
    assert_rank_choice_exists,
    login_as,
)
from gbetext import (
    default_volunteer_submit_msg,
    default_volunteer_no_bid_msg,
    default_volunteer_no_interest_msg,
    existing_volunteer_msg,
    no_profile_msg,
)
from gbe_forms_text import unavailable_time_conflict
from gbe.models import (
    AvailableInterest,
    Conference,
    Volunteer,
    VolunteerInterest,
    UserMessage,
)


class TestCreateVolunteer(TestCase):
    '''Tests for create_volunteer view'''
    view_name = 'volunteer_create'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.profile = ProfileFactory()
        Conference.objects.all().delete()
        UserMessage.objects.all().delete()
        AvailableInterest.objects.all().delete()
        self.conference = ConferenceFactory(accepting_bids=True)
        days = ConferenceDayFactory.create_batch(3, conference=self.conference)
        [VolunteerWindowFactory(day=day) for day in days]
        self.interest = AvailableInterestFactory()

    def get_volunteer_form(self, submit=False, invalid=False):
        form = {'profile': 1,
                'number_shifts': 2,
                'available_windows': self.conference.windows().values_list(
                    'pk', flat=True)[0:2],
                'unavailable_windows': self.conference.windows().values_list(
                    'pk', flat=True)[2],
                '%d-rank' % self.interest.pk: 4,
                '%d-interest' % self.interest.pk: self.interest.pk,
                'b_title': 'title',
                'background': 'background',
                }
        if submit:
            form['submit'] = True
        if invalid:
            del(form['number_shifts'])
        return form

    def post_volunteer_submission(self, data=None):
        if not data:
            data = self.get_volunteer_form(submit=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        num_volunteers_before = Volunteer.objects.count()
        response = self.client.post(url, data=data, follow=True)
        return response, num_volunteers_before

    def test_create_volunteer_no_login(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            "%s?next=%s" % (
                reverse('register', urlconf='gbe.urls'),
                url))

    def test_create_volunteer_bad_profile(self):
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

    def test_create_volunteer_post_valid_form(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        data = self.get_volunteer_form()
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_create_volunteer_post_form_invalid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        data = self.get_volunteer_form(invalid=True)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)

    def test_create_volunteer_no_post(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_create_volunteer_post_with_submit_is_true(self):
        response, num_volunteers_before = self.post_volunteer_submission()
        self.assertEqual(response.status_code, 200)
        self.assertIn('Profile View', response.content)
        self.assertEqual(num_volunteers_before + 1, Volunteer.objects.count())

    def test_create_volunteer_check_interest(self):
        response, num_volunteers_before = self.post_volunteer_submission()
        vol_interest = VolunteerInterest.objects.get(interest=self.interest)
        self.assertEqual(vol_interest.volunteer.profile, self.profile)

    def test_create_volunteer_with_get_request(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Volunteer', response.content)
        assert_rank_choice_exists(response, self.interest)
        assert_hidden_value(
            response,
            "id_b_title",
            "b_title",
            'volunteer bid: %s' % self.profile.display_name)

    def test_volunteer_submit_make_message(self):
        response, data = self.post_volunteer_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_volunteer_submit_msg)

    def test_volunteer_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeVolunteerView',
            code='SUBMIT_SUCCESS')
        response, data = self.post_volunteer_submission()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_no_biddable_conference(self):
        self.conference.accepting_bids = False
        self.conference.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'danger', 'Error', default_volunteer_no_bid_msg)

    def test_no_window_for_conference(self):
        Conference.objects.all().delete()
        ConferenceFactory(accepting_bids=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'danger', 'Error', default_volunteer_no_bid_msg)

    def test_no_interests(self):
        AvailableInterest.objects.all().delete()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'danger', 'Error', default_volunteer_no_bid_msg)

    def test_no_interests_has_message(self):
        msg = UserMessageFactory(
            view='MakeVolunteerView',
            code='NO_BIDDING_ALLOWED')
        AvailableInterest.objects.all().delete()
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'danger', 'Error', msg.description)

    def test_not_interested_at_all(self):
        data = self.get_volunteer_form(submit=True)
        data['%d-rank' % self.interest.pk] = 1
        response, data = self.post_volunteer_submission(data)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'danger', 'Error', default_volunteer_no_interest_msg)

    def test_not_interested_at_all_make_message(self):
        data = self.get_volunteer_form(submit=True)
        data['%d-rank' % self.interest.pk] = 1
        msg = UserMessageFactory(
            view='MakeVolunteerView',
            code='NO_INTERESTS_SUBMITTED')
        response, data = self.post_volunteer_submission(data)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'danger', 'Error', msg.description)

    def test_volunteer_time_conflict_checked(self):
        data = self.get_volunteer_form()
        data['available_windows'] = data['unavailable_windows']
        response, data = self.post_volunteer_submission(data=data)
        assert unavailable_time_conflict in response.content

    def test_create_second_volunteer_gets_redirect(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        volunteer = VolunteerFactory(
            profile=self.profile,
            b_conference=self.conference)
        login_as(self.profile, self)
        data = self.get_volunteer_form()
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(
            response,
            reverse(
                'volunteer_edit',
                urlconf='gbe.urls',
                args=[volunteer.id]))
        assert_alert_exists(
            response, 'success', 'Success', existing_volunteer_msg)

    def test_create_second_volunteer_old_conf_all_good(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        VolunteerFactory(profile=self.profile,
                         b_conference=ConferenceFactory(status='past'))
        login_as(self.profile, self)
        data = self.get_volunteer_form()
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_background_required(self):
        data = self.get_volunteer_form(submit=True)
        del data['background']
        response, data = self.post_volunteer_submission(data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("This field is required.", response.content)
