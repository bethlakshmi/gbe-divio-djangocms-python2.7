from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts.show_context import ShowContext


class TestTemplateList(TestCase):
    view_name = 'list_template'

    def setUp(self):
        self.client = Client()
        self.privileged_profile = ProfileFactory()
        self.url = reverse(self.view_name,
                           urlconf="gbe.email.urls")

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "%s/?next=%s" % (
            reverse('login', urlconf='gbe.urls'),
            self.url)
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_volunteer_coordinator(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)

        templates = ["volunteer accepted",
                     "volunteer duplicate",
                     "volunteer no decision",
                     "volunteer reject",
                     "volunteer schedule update",
                     "volunteer schedule warning",
                     "volunteer submission notification",
                     "volunteer update notification",
                     "volunteer wait list",
                     "volunteer withdrawn", ]
        for template in templates:
            self.assertContains(response, template)

    def test_act_coordinator(self):
        context = ShowContext()
        grant_privilege(self.privileged_profile.user_object,
                        'Act Coordinator')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)

        templates = ["act accepted - %s" % context.show.e_title.lower(),
                     "act duplicate",
                     "act no decision",
                     "act reject",
                     "act submission notification",
                     "act wait list",
                     "act withdrawn", ]
        for template in templates:
            self.assertContains(response, template)

    def test_basic_bid_coordinators(self):
        for bid_type in ['Class', 'Costume', 'Vendor']:
            grant_privilege(self.privileged_profile.user_object,
                            '%s Coordinator' % bid_type)
            login_as(self.privileged_profile, self)
            response = self.client.get(self.url)

            templates = ["%s accepted",
                         "%s duplicate",
                         "%s no decision",
                         "%s reject",
                         "%s submission notification",
                         "%s wait list",
                         "%s withdrawn", ]
            for template in templates:
                self.assertContains(response, template % bid_type.lower())

    def test_scheduler(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Scheduling Mavens')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, "daily schedule")
