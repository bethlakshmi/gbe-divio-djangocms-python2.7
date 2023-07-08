from django.urls import reverse
from django.test import TestCase, Client
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from gbe.models import Conference
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)


class TestReviewStaffArea(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()

    def test_review_staff_area_not_visible_without_permission(self):
        login_as(self.profile, self)
        current_conference = ConferenceFactory()
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls"))
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_review_staff_area_path(self):
        '''review_staff_area view should load
        '''
        current_conference = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls"))
        self.assertEqual(response.status_code, 200)

    def test_review_staff_area_by_conference(self):
        '''review_staff_area view should load
        '''
        Conference.objects.all().delete()
        conf = ConferenceFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls"),
            data={'conf_slug': conf.conference_slug})
        self.assertEqual(response.status_code, 200)

    def test_get_staff_area(self, ):
        context = StaffAreaContext()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls"),
            data={'conf_slug': context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, context.area.title)
        self.assertContains(response, context.area.staff_lead)
