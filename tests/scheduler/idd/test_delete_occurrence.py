from django.test import TestCase
from scheduler.idd import delete_occurrence
from tests.contexts import VolunteerContext


class TestDeleteOccurrence(TestCase):

    def setUp(self):
        self.context = VolunteerContext()

    def test_delete_bad_occurrence(self):
        response = delete_occurrence(self.context.opp_event.pk+1000)
        self.assertEqual(response.errors[0].code, "OCCURRENCE_NOT_FOUND")
