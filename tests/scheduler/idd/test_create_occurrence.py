from django.test import TestCase
from scheduler.idd import create_occurrence
from scheduler.models import Event
from datetime import (
    datetime,
    timedelta,
)
from tests.contexts import VolunteerContext


class TestCreateOccurrence(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.context = VolunteerContext()

    def setUp(self):
        self.max_pk = Event.objects.latest('pk').pk

    def test_bad_parent(self):
        response = create_occurrence(
            "bad parent",
            timedelta(minutes=60),
            "Volunteer",
            datetime.now(),
            parent_event_id=self.max_pk + 100,
            )
        self.assertEqual(response.errors[0].code,
                         "GET_PARENT_OCCURRENCE_NOT_FOUND")
        self.assertEqual(self.max_pk, Event.objects.latest('pk').pk)

    def test_bad_peer(self):
        response = create_occurrence(
            "bad peer",
            timedelta(minutes=60),
            "Volunteer",
            datetime.now(),
            peer_id=self.max_pk + 100,
            )
        self.assertEqual(response.errors[0].code,
                         "GET_PEER_OCCURRENCE_NOT_FOUND")
        self.assertEqual(self.max_pk, Event.objects.latest('pk').pk)
