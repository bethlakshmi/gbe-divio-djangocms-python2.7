from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.contexts import StaffAreaContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
    setup_admin_w_privs,
)
from gbe.models import Conference


class TestSpecialMenu(TestCase):
    '''Tests for special menu display'''
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

    def setUp(self):
        self.client = Client()
        self.url = reverse(
            "home",
            urlconf='gbe.urls')

    def test_privileged_views_get_leaf_menu(self):
        ''' each privilege should get the right lowest
            level menus URLs
        '''
        from gbe.special_privileges import special_menu_tree
        for privilege in self.special_roles:
            privileged_profile = ProfileFactory()
            grant_privilege(privileged_profile.user_object, privilege)
            login_as(privileged_profile, self)
            response = self.client.get(self.url)
            for menu_item in special_menu_tree:
                if privilege in menu_item['groups']:
                    self.assertContains(
                        response,
                        menu_item['url'],
                        status_code=200,
                        msg_prefix='Role %s gets url %s' % (
                            privilege, menu_item['url']))

    def test_privileged_views_test_load_page(self):
        ''' should always be able to all pages, even when conference not active
        '''
        from gbe.special_privileges import special_menu_tree
        Conference.objects.all().delete()
        ConferenceFactory(status='completed')

        privileged_profile = setup_admin_w_privs([]).profile
        grant_privilege(privileged_profile,
                        'Registrar',
                        'view_transaction')
        grant_privilege(privileged_profile,
                        'Ticketing - Admin',
                        'view_checklistitem')
        for privilege in self.special_roles:
            grant_privilege(privileged_profile.user_object, privilege)
            login_as(privileged_profile, self)

        for menu_item in special_menu_tree:
            if len(menu_item['url']) > 0:
                response = self.client.get(menu_item['url'])
                self.assertEqual(response.status_code, 200)

    def test_privileged_views_get_parent_menus(self):
        ''' each privilege should get the right parent menu
            these don't have urls, only titles
        '''
        from gbe.special_privileges import special_menu_tree
        for privilege in self.special_roles:
            privileged_profile = ProfileFactory()
            grant_privilege(privileged_profile.user_object, privilege)
            login_as(privileged_profile, self)
            response = self.client.get(self.url)
            for menu_item in special_menu_tree:
                if privilege in menu_item['groups']:
                    self.assertContains(
                        response,
                        menu_item['title'],
                        status_code=200,
                        msg_prefix='Role %s gets title %s' % (
                            privilege, menu_item['title']))

    def test_regular_users_get_nothing(self):
        ''' no group privilege, no special menus
        '''
        from gbe.special_privileges import special_menu_tree
        unprivileged_profile = ProfileFactory()
        login_as(unprivileged_profile, self)
        response = self.client.get(self.url)
        self.assertNotContains(
            response,
            'Special',
            status_code=200,
            msg_prefix='Normal users don\'t get a Special Menu'
        )
        for menu_item in special_menu_tree:
            if menu_item['url'] != '':
                self.assertNotContains(
                    response,
                    menu_item['url'],
                    msg_prefix='Normal users should not see %s' % (
                        menu_item['url']))

    def test_staff_get_menus(self):
        ''' each privilege should get the right lowest
            level menus URLs
        '''
        from gbe.special_privileges import special_menu_tree
        Conference.objects.all().delete()
        privilege = "Staff Lead"
        context = StaffAreaContext()
        login_as(context.staff_lead, self)
        response = self.client.get(self.url)
        for menu_item in special_menu_tree:
            if privilege in menu_item['groups']:
                self.assertContains(
                    response,
                    menu_item['url'],
                    status_code=200,
                    msg_prefix='Role %s gets url %s' % (
                        privilege, menu_item['url']))
                self.assertContains(
                    response,
                    menu_item['title'],
                    status_code=200,
                    msg_prefix='Role %s gets title %s' % (
                        privilege, menu_item['title']))

    def test_old_staff_lead_get_nothing(self):
        ''' no group privilege, no special menus
        '''
        from gbe.special_privileges import special_menu_tree
        Conference.objects.all().delete()
        privilege = "Staff Lead"
        context = StaffAreaContext()
        context.conference.status = "completed"
        context.conference.save()
        login_as(context.staff_lead, self)
        response = self.client.get(self.url)
        self.assertNotContains(
            response,
            'Special',
            status_code=200,
            msg_prefix='Normal users don\'t get a Special Menu'
        )
        for menu_item in special_menu_tree:
            if menu_item['url'] != '':
                self.assertNotContains(
                    response,
                    menu_item['url'],
                    msg_prefix='Normal users should not see %s' % (
                        menu_item['url']))

    def test_admin(self):
        from gbe.special_privileges import special_menu_tree
        privileged_user = setup_admin_w_privs(["Registrar"])
        login_as(privileged_user, self)
        response = self.client.get(self.url)
        for item in special_menu_tree:
            if 'admin_access' in item.keys() and item['admin_access']:
                self.assertContains(response, item['title'])
