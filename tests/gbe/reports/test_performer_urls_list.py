from pytz import utc
from django.urls import reverse
from django.test import TestCase, Client
from tests.contexts import ActTechInfoContext
from tests.factories.gbe_factories import (
    ActFactory,
    PersonaFactory,
    ProfileFactory,
    TechInfoFactory,
    TroupeFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.formats import date_format


class TestPerformerSlidesList(TestCase):
    '''Tests for index view'''
    view_name = 'performer_urls'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.context = ActTechInfoContext(schedule_rehearsal=True)
        cls.url1 = cls.context.set_social_media("Instagram")
        cls.url2 = cls.context.set_social_media()
        cls.profile = ProfileFactory()
        grant_privilege(cls.profile, 'Staff Lead')
        cls.url = reverse(cls.view_name,
                          urlconf='gbe.reporting.urls',
                          args=[cls.context.sched_event.pk])

    def test_review_privilege_fail(self):
        '''view should load for Tech Crew and fail for others '''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_review_bad_show(self):
        login_as(self.profile, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.pk+100]),
            follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))

    def test_review_2_urls(self):
        self.context.order_act(self.context.act, "3")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.context.act.performer))
        self.assertContains(response, self.url1.get_url())
        self.assertContains(response, self.url2.get_url())
        self.assertContains(response, "3")
