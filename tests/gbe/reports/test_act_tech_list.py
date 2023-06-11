from pytz import utc
from django.urls import reverse
from django.test import TestCase, Client
from tests.contexts import ActTechInfoContext
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
    TechInfoFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.formats import date_format


class TestReviewActTechInfo(TestCase):
    '''Tests for index view'''
    view_name = 'act_tech_list'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.context = ActTechInfoContext(schedule_rehearsal=True)
        cls.profile = ProfileFactory()
        grant_privilege(cls.profile, 'Staff Lead')
        cls.url = reverse(cls.view_name,
                          urlconf='gbe.reporting.urls',
                          args=[cls.context.sched_event.pk])
        cls.context.act.tech.introduction_text = "intro text"
        cls.context.act.tech.feel_of_act = "feel my act"
        cls.context.act.tech.read_exact = True
        cls.context.act.tech.prop_setup = "[u'I have props I will need ' + \
            'set before my number', u'I will leave props or set pieces ' + \
            'on-stage that will need to be cleared']"
        cls.context.act.tech.crew_instruct = "crew instruct"
        cls.context.act.performer.pronouns = "they/them"
        cls.context.act.tech.primary_color = "reds"
        cls.context.act.tech.secondary_color = "black"
        cls.context.act.tech.track = SimpleUploadedFile(
            "file.mp3",
            b"file_content")
        cls.context.act.tech.save()
        cls.context.act.performer.save()

    def test_review_act_tech_fail(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_review_act_tech_bad_show(self):
        login_as(self.profile, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.pk+100]),
            follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))

    def test_review_act_tech_the_basics(self):
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.act.b_title)
        self.assertContains(response, str(self.context.act.performer))
        self.assertContains(response, self.context.act.tech.introduction_text)
        self.assertContains(response, "Yes")
        self.assertContains(
            response,
            'I have props I will need set before my number')
        self.assertContains(
            response,
            'I will leave props or set pieces on-stage that will need to ' +
            'be cleared')
        self.assertContains(response, self.context.act.tech.crew_instruct)
        self.assertContains(response, self.context.act.performer.pronouns)
        self.assertContains(response, self.context.act.tech.primary_color)
        self.assertContains(response, self.context.act.tech.secondary_color)
        self.assertContains(response, 'OFF')

    def test_review_act_tech_advanced(self):
        self.context.act.tech.prop_setup = ""
        self.context.act.tech.mic_choice = "I own a mic"
        self.context.act.tech.background_color = "blue"
        self.context.act.tech.wash_color = "green"
        self.context.act.tech.follow_spot_color = "purple"
        self.context.act.tech.special_lighting_cue = "this is my cue"
        self.context.act.tech.start_blackout = True
        self.context.act.tech.end_blackout = True
        self.context.act.tech.confirm_no_music = True
        self.context.act.tech.save()

        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.act.tech.mic_choice)
        self.assertContains(response, self.context.act.tech.background_color)
        self.assertContains(response, self.context.act.tech.wash_color)
        self.assertContains(response, self.context.act.tech.follow_spot_color)
        self.assertContains(response,
                            self.context.act.tech.special_lighting_cue)
        self.assertContains(response, "Blackout", 2)
        self.assertNotContains(
            response,
            'I have props I will need set before my number')
        self.assertContains(response, "no music")

    def test_review_act_techinfo_order(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        self.context.order_act(self.context.act, "3")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, "3")
        self.assertContains(response, self.context.order.role)
