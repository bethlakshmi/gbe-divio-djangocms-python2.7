from django.test import TestCase
from scheduler.idd import update_occurrence
from scheduler.models import Event
from datetime import (
    datetime,
    timedelta,
)
from tests.contexts import VolunteerContext


class TestUpdateOccurrence(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.context = VolunteerContext()

    def setUp(self):
        self.max_pk = Event.objects.latest('pk').pk

    def test_bad_id(self):
        response = update_occurrence(
            self.context.opp_event.pk+100,
            "bad parent",
            )
        self.assertEqual(response.errors[0].code,
                         "OCCURRENCE_NOT_FOUND")

    def test_bad_parent(self):
        response = update_occurrence(
            self.context.opp_event.pk,
            "bad parent",
            parent_event_id=self.max_pk + 100,
            )
        self.assertEqual(response.errors[0].code,
                         "GET_PARENT_OCCURRENCE_NOT_FOUND")

    def test_bad_peer(self):
        response = update_occurrence(
            self.context.opp_event.pk,
            "bad peer",
            peer_id=self.max_pk + 100,
            )
        self.assertEqual(response.errors[0].code,
                         "GET_PEER_OCCURRENCE_NOT_FOUND")
