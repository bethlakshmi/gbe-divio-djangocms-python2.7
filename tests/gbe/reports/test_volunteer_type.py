from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
    ShowFactory,
)
from gbe.models import Conference
from tests.contexts import VolunteerContext


class TestVolunteerTypeArea(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()

    def test_volunteer_type_path(self):
        '''staff_area view should load
        '''
        show = ShowFactory()
        context = VolunteerContext(event=show)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('volunteer_type',
                    urlconf="gbe.reporting.urls",
                    args=[context.opportunity.e_conference.conference_slug,
                          context.interest.interest.pk]))
        self.assertEqual(response.status_code, 200)

    def test_volunteer_type_with_inactive(self):
        '''staff_area view should load
        '''
        show = ShowFactory()
        inactive = ProfileFactory(
            display_name="DON'T SEE THIS",
            user_object__is_active=False
        )
        context = VolunteerContext(event=show, profile=inactive)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('volunteer_type',
                    urlconf="gbe.reporting.urls",
                    args=[context.opportunity.e_conference.conference_slug,
                          context.interest.interest.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            '<tr style="color:red;">' in response.content)

    def test_volunteer_type_path_fail(self):
        '''staff_area view should fail for non-authenticated users
        '''
        show = ShowFactory()
        context = VolunteerContext(event=show)
        login_as(self.profile, self)
        response = self.client.get(
            reverse('volunteer_type',
                    urlconf="gbe.reporting.urls",
                    args=[context.opportunity.e_conference.conference_slug,
                          context.interest.interest.pk]))
        self.assertEqual(response.status_code, 403)

    def test_volunteer_type_bad_type(self):
        '''staff_area view should fail for non-authenticated users
        '''
        show = ShowFactory()
        context = VolunteerContext(event=show)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('volunteer_type',
                    urlconf="gbe.reporting.urls",
                    args=[context.opportunity.e_conference.conference_slug,
                          context.interest.interest.pk+100]))
        self.assertEqual(response.status_code, 404)
