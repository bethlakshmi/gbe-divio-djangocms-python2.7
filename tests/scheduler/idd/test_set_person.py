from django.test import TestCase
from scheduler.idd import set_person


class TestSetPerson(TestCase):

    def test_no_arguments(self):
        response = set_person()
        self.assertEqual(response.errors[0].code, "OCCURRENCE_NOT_FOUND")
        self.assertEqual(
            response.errors[0].details,
            "Neither booking id nor occurrence id provided")
