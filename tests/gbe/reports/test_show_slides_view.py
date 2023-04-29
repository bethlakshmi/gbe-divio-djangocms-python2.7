from django.urls import reverse
from django.test import TestCase, Client
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import ProfileFactory
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    SchedEventFactory,
)
from tests.contexts import ActTechInfoContext
from gbetext import role_commit_map


class TestShowSlidesView(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfileFactory()
        grant_privilege(cls.profile, 'Slide Helper')
        cls.context = ActTechInfoContext(schedule_rehearsal=True)
        cls.url1 = cls.context.set_social_media("Instagram")
        cls.url2 = cls.context.set_social_media()
        cls.url = reverse('show_slide_list', urlconf="gbe.reporting.urls")

    def test_no_priv(self):
        regular_profile = ProfileFactory()
        login_as(regular_profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_default_display(self):
        '''staff_area view should load only the actually assigned volunteer
        '''
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.sched_event.title)
        self.assertContains(response, reverse(
            'performer_urls',
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.pk]))
