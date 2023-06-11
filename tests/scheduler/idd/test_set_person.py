from django.test import TestCase
from scheduler.idd import set_person
from tests.contexts import ClassContext
from scheduler.data_transfer import Person


class TestSetPerson(TestCase):

    def setUp(self):
        self.context = ClassContext()

    def test_no_arguments(self):
        response = set_person()
        self.assertEqual(response.errors[0].code, "OCCURRENCE_NOT_FOUND")
        self.assertEqual(
            response.errors[0].details,
            "Neither booking id nor occurrence id provided")

    def test_set_person_no_public_class(self):
        response = set_person(self.context.sched_event.pk, Person(
            users=[self.context.teacher.contact.user_object],
            role="Teacher"))
        self.assertEqual(response.errors[0].code,
                         "LINKED_CLASS_AND_ID_REQUIRED")
