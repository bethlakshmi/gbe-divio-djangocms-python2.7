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

    @classmethod
    def setUpTestData(cls):
        cls.priv_profile = ProfileFactory()
        cls.context = ClassContext()
        cls.old_conference = ConferenceFactory(status="completed")
        cls.old_context = ClassContext(conference=cls.old_conference)
        grant_privilege(cls.priv_profile, 'Class Coordinator')
        cls.url = reverse(cls.view_name, urlconf="gbe.reporting.urls")

    def test_not_visible_without_permission(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_default_conf_success(self):
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.context.bid.b_title)
        self.assertNotContains(response, self.old_context.bid.b_title)
        self.assertContains(response, self.context.teacher.name)
        self.assertNotContains(response, self.old_context.teacher.name)
        self.assertContains(response, eval_report_explain_msg)

    def test_old_conf_success(self):
        login_as(self.priv_profile, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.old_context.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.context.bid.b_title)
        self.assertContains(response, self.old_context.bid.b_title)
        self.assertNotContains(response, self.context.teacher.name)
        self.assertContains(response, self.old_context.teacher.name)

    def test_interest_no_evals(self):
        interested = []
        for i in range(0, 3):
            interested += [self.context.set_interest()]
        login_as(self.priv_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td>3</td>')
        self.assertContains(response, '<td>0</td>')
        self.assertNotContains(response, reverse(
            'evaluation_detail',
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.id]))

    def test_summary_calculations(self):
        interested = []
        login_as(self.priv_profile, self)
        grade1 = EventEvalGradeFactory(event=self.context.sched_event,
                                       answer=4)
        ProfileFactory(user_object=grade1.user)
        grade2 = EventEvalGradeFactory(event=self.context.sched_event,
                                       answer=3,
                                       question=grade1.question)
        ProfileFactory(user_object=grade2.user)
        bool1 = EventEvalBooleanFactory(event=self.context.sched_event,
                                        answer=True,
                                        user=grade1.user)
        bool2 = EventEvalBooleanFactory(event=self.context.sched_event,
                                        answer=False,
                                        user=grade2.user,
                                        question=bool1.question)
        text1 = EventEvalCommentFactory(event=self.context.sched_event,
                                        user=grade1.user)
        text2 = EventEvalCommentFactory(event=self.context.sched_event,
                                        user=grade2.user,
                                        question=text1.question)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td>0</td>')
        self.assertContains(response, '<td>2</td>')
        self.assertContains(response, grade1.question.question)
        self.assertNotContains(response, bool1.question.question)
        self.assertNotContains(response, text1.question.question)
        self.assertContains(response, '<td>3.5</td>')
        self.assertNotContains(response, '<td>0.5</td>')
        self.assertContains(response, reverse(
            'evaluation_detail',
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.id]))

    def test_details(self):
        interested = []
        login_as(self.priv_profile, self)
        grade1 = EventEvalGradeFactory(event=self.context.sched_event,
                                       answer=4)
        ProfileFactory(user_object=grade1.user)
        grade2 = EventEvalGradeFactory(event=self.context.sched_event,
                                       answer=3,
                                       question=grade1.question)
        ProfileFactory(user_object=grade2.user)
        bool1 = EventEvalBooleanFactory(event=self.context.sched_event,
                                        answer=True,
                                        user=grade1.user)
        bool2 = EventEvalBooleanFactory(event=self.context.sched_event,
                                        answer=False,
                                        user=grade2.user,
                                        question=bool1.question)
        text1 = EventEvalCommentFactory(event=self.context.sched_event,
                                        user=grade1.user)
        text2 = EventEvalCommentFactory(event=self.context.sched_event,
                                        user=grade2.user,
                                        question=text1.question)

        response = self.client.get(reverse(
            'evaluation_detail',
            urlconf='gbe.reporting.urls',
            args=[self.context.sched_event.id]))
        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, grade1.question.question, 5)
        self.assertContains(response, bool1.question.question, 2)
        self.assertContains(response, text1.question.question, 2)
        self.assertContains(response, grade1.user.profile.display_name)
        self.assertContains(response, grade2.user.profile.display_name)
        self.assertContains(response, '<td>4</td>')
        self.assertContains(response, '<td>3</td>')
        self.assertContains(response, self.context.bid.b_description)

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
