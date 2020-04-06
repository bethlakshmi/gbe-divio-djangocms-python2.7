from pytz import utc
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from tests.contexts import ActTechInfoContext
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.formats import date_format


class TestReviewActTechInfo(TestCase):
    '''Tests for index view'''
    view_name = 'act_techinfo_detail'

    def set_the_basics(self):
        self.context.act.tech.introduction_text = "intro text"
        self.context.act.tech.feel_of_act = "feel my act"
        self.context.act.tech.read_exact = True
        self.context.act.tech.prop_setup = "[u'I have props I will need ' + \
            'set before my number', u'I will leave props or set pieces ' + \
            'on-stage that will need to be cleared']"
        self.context.act.tech.crew_instruct = "crew instruct"
        self.context.act.tech.pronouns = "these are my pronouns"
        self.context.act.tech.primary_color = "reds"
        self.context.act.tech.secondary_color = "black"
        self.context.act.tech.track = SimpleUploadedFile(
            "file.mp3",
            "file_content")
        self.context.act.tech.save()

    def setUp(self):
        self.context = ActTechInfoContext(schedule_rehearsal=True)
        self.client = Client()
        self.profile = ProfileFactory()
        grant_privilege(self.profile, 'Tech Crew')
        self.url = reverse(self.view_name,
                           urlconf='gbe.reporting.urls',
                           args=[self.context.act.id])

    def test_review_act_techinfo_fail(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        profile = ProfileFactory()
        login_as(profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_review_act_techinfo_bad_act(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        login_as(self.profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf='gbe.reporting.urls',
                                           args=[self.context.act.id+1]),
                                   follow=True)
        self.assertEqual(response.status_code, 404)

    def test_review_act_techinfo_the_basics(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        self.set_the_basics()
        login_as(self.profile, self)
        response = self.client.get(self.url)
        print response
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.act.b_title)
        self.assertContains(response, str(self.context.act.performer))
        self.assertContains(response, str(
            self.context.act.performer.contact.user_object.email))
        self.assertContains(response, str(self.context.show))
        self.assertContains(response, self.context.act.tech.introduction_text)
        self.assertContains(response, self.context.act.tech.feel_of_act)
        self.assertContains(response, "Read this exacty")
        self.assertContains(
            response,
            'I have props I will need set before my number')
        self.assertContains(
            response,
            'I will leave props or set pieces on-stage that will need to ' +
            'be cleared')
        self.assertContains(response, self.context.act.tech.crew_instruct)
        self.assertContains(response, self.context.act.tech.pronouns)
        self.assertContains(response, self.context.act.tech.primary_color)
        self.assertContains(response, self.context.act.tech.secondary_color)
        self.assertContains(response, self.context.act.tech.pronouns)
        self.assertContains(response, self.context.act.tech.track.url)
        self.assertContains(response, '<b>Follow Spot:</b> OFF<br>')
        self.assertContains(response, date_format(
            self.context.rehearsal.start_time,
            "DATETIME_FORMAT"))

    def test_review_act_techinfo_advanced(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        self.set_the_basics()
        self.context.act.tech.mic_choice = "I own a mic"
        self.context.act.tech.background_color = "blue"
        self.context.act.tech.wash_color = "green"
        self.context.act.tech.follow_spot_color = "purple"
        self.context.act.tech.special_lighting_cue = "this is my cue"
        self.context.act.tech.start_blackout = True
        self.context.act.tech.end_blackout = True
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
        self.assertContains(response, "<b>Starting Lights:</b> Blackout")
        self.assertContains(response, "<b>Lighting at End:</b> Blackout")

    def test_review_act_techinfo_incomplete(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, "Act Tech is NOT complete")

    def test_withdrawn_act(self):
        act = ActFactory(accepted=4)
        login_as(self.profile, self)
        response = self.client.get(reverse(self.view_name,
                                           urlconf='gbe.reporting.urls',
                                           args=[act.id]))
        self.assertContains(response, "Act state is Withdrawn")

    def test_review_act_techinfo_order(self):
        '''review_act_techinfo view should load for Tech Crew
           and fail for others
        '''
        self.context.order_act(self.context.act, "3")
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, "3<br></span><br>Show Order</div>")
