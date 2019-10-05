from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    AvailableInterestFactory,
    ConferenceFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    VolunteerFactory,
    VolunteerInterestFactory
)
from tests.functions.gbe_functions import (
    assert_interest_view,
    bad_id_for,
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts.volunteer_context import VolunteerContext
from gbe.models import Volunteer
from gbetext import states_options


class TestReviewVolunteer(TestCase):
    '''Tests for review_volunteer view'''
    view_name = 'volunteer_review'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')
        self.coordinator = ProfileFactory()
        grant_privilege(self.coordinator, 'Volunteer Reviewers')
        grant_privilege(self.coordinator, 'Volunteer Coordinator')

    def get_form(self, bid, evaluator, invalid=False):
        data = {'vote': 3,
                'notes': "Foo",
                'bid': bid.pk,
                'evaluator': evaluator.pk}
        if invalid:
            del(data['vote'])
        return data

    def test_review_volunteer_all_well(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Change Bid State:' in response.content)

    def test_review_volunteer_get_conference(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(
            url,
            data={'conf_slug': volunteer.b_conference.id})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
        self.assertTrue('Review Information' in response.content)
        self.assertContains(response, '<h3> %s </h3>' %
                            volunteer.b_conference.conference_name)

    def test_review_volunteer_coordinator(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Change Bid State:' in response.content)
        self.assertTrue('Bid Information' in response.content)
        self.assertTrue('Review Information' in response.content)

    def test_review_volunteer_post_invalid(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        data = self.get_form(volunteer, self.coordinator, invalid=True)
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Change Bid State:' in response.content)
        self.assertTrue('Bid Information' in response.content)

    def test_review_volunteer_post_valid(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.coordinator, self)
        data = self.get_form(volunteer, self.coordinator)
        response = self.client.post(url, data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        html_tag = '<h2 class="review-title">%s</h2>'
        title_string = ("Bid Information for %s" %
                        volunteer.b_conference.conference_name)
        html_title = html_tag % title_string
        assert html_title in response.content

    def test_review_volunteer_past_conference(self):
        conference = ConferenceFactory(status='completed')
        volunteer = VolunteerFactory(b_conference=conference)
        url = reverse(self.view_name, args=[volunteer.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[volunteer.pk]))
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Review Information' in response.content)

    def test_no_login_gives_error(self):
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_vendor_id(self):
        login_as(ProfileFactory(), self)
        bad_id = bad_id_for(Volunteer)
        url = reverse(self.view_name, args=[bad_id], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_review_volunteer_fetch_by_post(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[0],
                      urlconf='gbe.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(url, data={'volunteer': volunteer.pk})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Change Bid State:' in response.content)

    def test_review_volunteer_with_interest(self):
        volunteer = VolunteerFactory()
        interest = VolunteerInterestFactory(
            volunteer=volunteer,
            interest=AvailableInterestFactory(
                help_text="help!"
            ))
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        assert_interest_view(response, interest)

    def test_review_volunteer_clean_available_windows(self):
        context = VolunteerContext()
        context.bid.available_windows.add(context.window)
        context.bid.save()
        not_there = context.add_window()
        url = reverse(self.view_name,
                      args=[context.bid.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertTrue(str(context.window) in response.content)
        self.assertTrue(str(not_there) not in response.content)

    def test_review_volunteer_clean_unavailable_windows(self):
        context = VolunteerContext()
        context.bid.unavailable_windows.add(context.window)
        context.bid.save()
        not_there = context.add_window()
        url = reverse(self.view_name,
                      args=[context.bid.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertTrue(str(context.window) in response.content)
        self.assertTrue(str(not_there) not in response.content)

    def test_review_volunteer_clean_state(self):
        volunteer = VolunteerFactory()
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        state_dict = dict(states_options)
        self.assertTrue(
            state_dict[volunteer.profile.state] in response.content)
        self.assertTrue(state_dict["CA"] not in response.content)

    def test_review_volunteer_clean_how_heard(self):
        profile = ProfileFactory(how_heard=['Word of mouth'])
        volunteer = VolunteerFactory(profile=profile)
        url = reverse(self.view_name,
                      args=[volunteer.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertTrue(profile.how_heard[0] in response.content)
        self.assertTrue("Attended Previously" not in response.content)
