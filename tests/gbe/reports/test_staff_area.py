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
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)


class TestStaffArea(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()

    def test_staff_area_path(self):
        '''staff_area view should load
        '''
        show = ShowFactory()
        context = VolunteerContext(event=show)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            "%s?area=Show" %
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=[show.eventitem_id]))
        self.assertEqual(response.status_code, 200)

    def test_show_with_inactive(self):
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
            "%s?area=Show" %
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=[show.eventitem_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            '<tr style="color:red;">' in response.content)

    def test_staff_area_path_fail(self):
        '''staff_area view should fail for non-authenticated users
        '''
        show = ShowFactory()
        login_as(self.profile, self)
        response = self.client.get(
            "%s?area=Show" %
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=[show.eventitem_id]))
        self.assertEqual(response.status_code, 403)

    def test_show_bad_event(self):
        show = ShowFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            "%s?area=Show" %
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=[show.eventitem_id+100]))
        self.assertContains(response,
                            "Staff Schedules for None")

    def test_staff_area_bad_area(self):
        '''staff_area view should fail for non-privileged users
        '''
        context = StaffAreaContext()
        login_as(self.profile, self)
        response = self.client.get(
            "%s?area=Staff" %
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=[context.area.pk+100]), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_staff_area_with_inactive(self):
        '''staff_area view should load
        '''
        context = StaffAreaContext()
        inactive = ProfileFactory(
            display_name="DON'T SEE THIS",
            user_object__is_active=False
        )
        vol, opp = context.book_volunteer(volunteer=inactive)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            "%s?area=Staff" %
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=[context.area.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            '<tr style="color:red;">' in response.content)
