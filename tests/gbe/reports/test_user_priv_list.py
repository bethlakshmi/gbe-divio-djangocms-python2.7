from pytz import utc
from django.urls import reverse
from django.test import TestCase
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
    TechInfoFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    setup_admin_w_privs,
    login_as,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.formats import date_format


class TestUserPrivList(TestCase):
    '''Tests for index view'''
    view_name = 'user_privs'

    special_roles = [
        'Act Reviewers',
        'Act Coordinator',
        'Admins',
        'Class Reviewers',
        'Class Coordinator',
        'Costume Reviewers',
        'Costume Coordinator',
        'Volunteer Reviewers',
        'Volunteer Coordinator',
        'Vendor Reviewers',
        'Vendor Coordinator',
        'Scheduling Mavens',
        'Slide Helper',
        'Stage Manager',
        'Tech Crew',
        'Theme Editor',
        'Ticketing - Admin',
        'Ticketing - Transactions',
        'Registrar'
    ]

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = setup_admin_w_privs(['Registrar'])
        cls.profile = ProfileFactory()
        cls.everything_user = ProfileFactory()
        for privilege in cls.special_roles:
            grant_privilege(cls.everything_user.user_object, privilege)

        grant_privilege(cls.profile, 'Act Coordinator')
        cls.url = reverse(cls.view_name,
                          urlconf='gbe.reporting.urls')

    def test_review_priv_fail(self):
        '''view should load for Admins and fail for anyone else'''
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, "/admin/login/?next=%s" % self.url)

    def test_review_the_basics(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for privilege in self.special_roles:
            self.assertContains(response, "<h3>%s</h3>" % privilege)
        self.assertContains(response, "<h3>Superusers (Admin setting)</h3>")
        self.assertContains(response, self.everything_user)
        self.assertContains(response, self.profile)
        self.assertContains(response, "<i>Admin</i>")

    def test_review_staff_lead(self):
        context = StaffAreaContext()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, context.staff_lead)
        self.assertContains(response, "<td>Staff Lead<br></td>")

    def test_review_booked_lead(self):
        context = VolunteerContext()
        booked_lead = context.set_staff_lead(role="Producer")
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, booked_lead)
        self.assertContains(response, "<td>Producer<br></td>")

    def test_missing_group_in_parent(self):
        from gbe.special_privileges import special_menu_tree
        special_menu_tree += [{
            'title': 'Missing Group',
            'url': reverse('list_template', urlconf='gbe.email.urls'),
            'parent_id': 10,
            'id': 3,
            'groups': ['Extra']}]
        grant_privilege(self.everything_user.user_object, 'Extra')
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(
            response,
            "menu: Missing Group, group: Extra - parent not found")

    def test_missing_group(self):
        from gbe.special_privileges import special_menu_tree
        special_menu_tree += [{
            'title': 'Missing Child',
            'url': reverse('list_template', urlconf='gbe.email.urls'),
            'parent_id': 10,
            'id': 3,
            'groups': ['More Extra']}]
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response,
                            "group: More Extra - not a configured group")
