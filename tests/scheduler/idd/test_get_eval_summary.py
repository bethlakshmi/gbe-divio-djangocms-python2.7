from django.test import TestCase
from scheduler.idd import get_eval_summary
from tests.factories.scheduler_factories import EventEvalQuestionFactory
from scheduler.models import EventEvalQuestion


class TestGetEvalSummary(TestCase):

    def setUp(self):
        EventEvalQuestion.objects.all().delete()

    def test_get_invisible_question(self):
        self.question = EventEvalQuestionFactory(visible=False)
        response = get_eval_summary([], visible=False)
        self.assertEqual(response.questions.first(), self.question)
