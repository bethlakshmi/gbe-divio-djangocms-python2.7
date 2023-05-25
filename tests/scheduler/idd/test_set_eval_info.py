from django.test import TestCase
from scheduler.idd import set_eval_info
from tests.contexts import ClassContext
from datetime import (
    datetime,
    timedelta,
)
from scheduler.data_transfer import Person
from tests.factories.gbe_factories import UserFactory


class TestSetEvalInfo(TestCase):

    def setUp(self):
        self.context = ClassContext(
            starttime=datetime.now()+timedelta(days=5))

    def test_get_bad_occurrence(self):
        response = set_eval_info(
            answers=[],
            occurrence_id=self.context.sched_event.pk+1000,
            person=None)
        self.assertEqual(response.errors[0].code, "OCCURRENCE_NOT_FOUND")

    def test_future_occurrence(self):
        response = set_eval_info(
            answers=[],
            occurrence_id=self.context.sched_event.pk,
            person=None)
        self.assertEqual(response.warnings[0].code, "EVENT_IN_FUTURE")

    def test_multiple_user_check(self):
        now_context = ClassContext()
        response = set_eval_info(
            answers=[],
            occurrence_id=now_context.sched_event.pk,
            person=Person(users=[UserFactory(), UserFactory()]))
        self.assertEqual(response.errors[0].code, "MORE_THAN_ONE_USER")
