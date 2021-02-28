from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    PersonaFactory,
    ProfilePreferencesFactory,
    ProfileFactory,
    StaffAreaFactory,
    UserMessageFactory,
    VolunteerFactory,
    VolunteerInterestFactory
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    WorkerFactory,
    ResourceAllocationFactory,
)
from tests.contexts import (
    VolunteerContext,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_rank_choice_exists,
    clear_conferences,
    login_as,
    grant_privilege,
)
from gbetext import (
    default_volunteer_edit_msg,
    default_volunteer_no_interest_msg
)
from gbe_forms_text import volunteer_labels
from gbe.models import UserMessage
from settings import GBE_DATETIME_FORMAT
from django.core import mail
from tests.gbe.test_gbe import TestGBE


class TestEditVolunteer(TestGBE):
    '''Tests for edit_volunteer view'''
    view_name = 'volunteer_edit'

    # this test case should be unnecessary, since edit_volunteer should go away
    # for now, test it.

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Volunteer Coordinator')
        grant_privilege(self.privileged_user, 'Volunteer Reviewers')

    def get_form(self, context, invalid=False, rank=5):
        interest_pk = context.bid.volunteerinterest_set.first().pk
        avail_pk = context.bid.volunteerinterest_set.first().interest.pk
        form = {'profile': 1,
                'number_shifts': 2,
                'availability': ('SH0',),
                'background': 'this is the background',
                'b_title': 'title',
                'pre_event': False,
                '%d-rank' % interest_pk: rank,
                '%d-interest' % interest_pk: avail_pk,
                'submit': True,
                }
        if invalid:
            del(form['number_shifts'])
        return form

    def edit_volunteer(self, rank=5):
        clear_conferences()
        pref = ProfilePreferencesFactory()
        context = VolunteerContext(profile=pref.profile)
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(self.privileged_user, self)
        form = self.get_form(context, rank=rank)
        response = self.client.post(
            url,
            form,
            follow=True)
        return response, context

    def test_edit_volunteer_no_volunteer(self):
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[0])
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_edit_volunteer_profile_is_not_coordinator(self):
        user = ProfileFactory().user_object
        volunteer = VolunteerFactory()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[volunteer.pk])
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertEqual(403, response.status_code)

    def test_edit_volunteer_profile_is_owner(self):
        context = VolunteerContext()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(context.profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, volunteer_labels['background'])

    def test_volunteer_edit_post_form_not_valid(self):
        # volunteer_edit, if form not valid, should return
        # to VolunteerEditForm
        context = VolunteerContext()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(self.privileged_user, self)
        response = self.client.post(
            url,
            self.get_form(context,
                          invalid=True))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Volunteer at the Expo')

    def test_volunteer_edit_post_form_valid(self):
        # volunteer_edit, if form not valid, should return
        # to VolunteerEditForm
        response, context = self.edit_volunteer()
        expected_string = ("Bid Information for %s" %
                           context.conference.conference_name)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, expected_string)

    def test_volunteer_edit_get(self):
        context = VolunteerContext()
        context.bid.b_title = "myTitle"
        context.bid.save()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Volunteer at the Expo')
        self.assert_hidden_value(
            response,
            "id_b_title",
            "b_title",
            context.bid.b_title)

    def test_volunteer_edit_get_rank(self):
        context = VolunteerContext()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        assert_rank_choice_exists(
            response,
            context.interest,
            context.interest.rank)

    def test_volunteer_edit_get_with_stuff(self):
        clear_conferences()
        context = VolunteerContext()
        url = reverse('volunteer_edit',
                      urlconf='gbe.urls',
                      args=[context.bid.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, volunteer_labels['background'])

    def test_volunteer_submit_make_message(self):
        response, context = self.edit_volunteer()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', default_volunteer_edit_msg)

    def test_volunteer_submit_has_message(self):
        msg = UserMessageFactory(
            view='MakeVolunteerView',
            code='EDIT_SUCCESS')
        response, context = self.edit_volunteer()
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_not_interested_at_all(self):
        response, context = self.edit_volunteer(rank=1)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'danger', 'Error', default_volunteer_no_interest_msg)

    def test_not_interested_at_all_make_message(self):
        msg = UserMessageFactory(
            view='MakeVolunteerView',
            code='NO_INTERESTS_SUBMITTED')
        response, context = self.edit_volunteer(rank=1)
        self.assertEqual(response.status_code, 200)
        assert_alert_exists(
            response, 'danger', 'Error', msg.description)

    def test_interest_bad_data(self):
        response, context = self.edit_volunteer(rank='bad_data')
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<font class="gbe-form-error"><ul class="errorlist">' +
            '<li>Select a valid choice. bad_data is not one of ' +
            'the available choices.</li></ul></font>',
            html=True)
