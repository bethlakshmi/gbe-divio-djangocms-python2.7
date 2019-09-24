from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory,
)
from tests.contexts import ClassContext
from gbe.models import Conference
from gbetext import eval_report_explain_msg
from tests.factories.scheduler_factories import (
    EventEvalGradeFactory,
    EventEvalBooleanFactory,
    EventEvalCommentFactory,
)


class TestEval(TestCase):
    view_name = "evaluation"

    def setUp(self):
        self.client = Client()
        self.priv_profile = ProfileFactory()
        self.context = ClassContext()
        self.old_conference = ConferenceFactory(status="completed")
        self.old_context = ClassContext(conference=self.old_conference)
        grant_privilege(self.priv_profile, 'Class Coordinator')
        self.url = reverse(self.view_name,
                           urlconf="gbe.reporting.urls")

    def test_not_visible_without_permission(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_default_conf_success(self):
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.bid.e_title)
        self.assertNotContains(response, self.old_context.bid.e_title)
        self.assertContains(response, self.context.teacher.name)
        self.assertNotContains(response, self.old_context.teacher.name)
        self.assertContains(response, eval_report_explain_msg)

    def test_old_conf_success(self):
        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.old_context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.context.bid.e_title)
        self.assertContains(response, self.old_context.bid.e_title)
        self.assertNotContains(response, self.context.teacher.name)
        self.assertContains(response, self.old_context.teacher.name)

    def test_interest_no_evals(self):
        interested = []
        for i in range(0, 3):
            interested += [self.context.set_interest()]
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td class="bid-table">3</td>')
        self.assertContains(response, '<td class="bid-table">0</td>')
        self.assertNotContains(response, reverse(
            'evaluation_detail',
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.id]))

    def test_summary_calculations(self):
        interested = []
        login_as(self.priv_profile, self)
        grade1 = EventEvalGradeFactory(event=self.context.sched_event,
                                       answer=4)
        grade2 = EventEvalGradeFactory(event=self.context.sched_event,
                                       answer=3,
                                       question=grade1.question)
        bool1 = EventEvalBooleanFactory(event=self.context.sched_event,
                                        answer=True,
                                        profile=grade1.profile)
        bool2 = EventEvalBooleanFactory(event=self.context.sched_event,
                                        answer=False,
                                        profile=grade2.profile,
                                        question=bool1.question)
        text1 = EventEvalCommentFactory(event=self.context.sched_event,
                                        profile=grade1.profile)
        text2 = EventEvalCommentFactory(event=self.context.sched_event,
                                        profile=grade2.profile,
                                        question=text1.question)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td class="bid-table">0</td>')
        self.assertContains(response, '<td class="bid-table">2</td>')
        self.assertContains(response, grade1.question.question)
        self.assertContains(response, bool1.question.question)
        self.assertNotContains(response, text1.question.question)
        self.assertContains(response, '<td class="bid-table">3.5</td>')
        self.assertContains(response, '<td class="bid-table">0.5</td>')
        self.assertContains(response, reverse(
            'evaluation_detail',
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.id]))

    def test_details(self):
        interested = []
        login_as(self.priv_profile, self)
        grade1 = EventEvalGradeFactory(event=self.context.sched_event,
                                       answer=4)
        grade2 = EventEvalGradeFactory(event=self.context.sched_event,
                                       answer=3,
                                       question=grade1.question)
        bool1 = EventEvalBooleanFactory(event=self.context.sched_event,
                                        answer=True,
                                        profile=grade1.profile)
        bool2 = EventEvalBooleanFactory(event=self.context.sched_event,
                                        answer=False,
                                        profile=grade2.profile,
                                        question=bool1.question)
        text1 = EventEvalCommentFactory(event=self.context.sched_event,
                                        profile=grade1.profile)
        text2 = EventEvalCommentFactory(event=self.context.sched_event,
                                        profile=grade2.profile,
                                        question=text1.question)

        response = self.client.get(reverse(
            'evaluation_detail',
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, grade1.question.question, 5)
        self.assertContains(response, bool1.question.question, 5)
        self.assertContains(response, text1.question.question, 2)
        self.assertContains(response, grade1.profile.profile.display_name)
        self.assertContains(response, grade2.profile.profile.display_name)
        self.assertContains(response, '<td class="bid-table">4</td>')
        self.assertContains(response, '<td class="bid-table">3</td>')
        self.assertContains(response, self.context.bid.e_description)

    def test_bad_details(self):
        interested = []
        login_as(self.priv_profile, self)

        response = self.client.get(reverse(
            'evaluation_detail',
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.id+100]))
        self.assertContains(
            response,
            "Occurrence id %d not found" % (self.context.sched_event.pk+100))
