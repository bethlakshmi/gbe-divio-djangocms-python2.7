from django.test import TestCase
from scheduler.idd import get_people
from tests.contexts import (
    ShowContext,
    VolunteerContext,
)
from tests.factories.scheduler_factories import LabelFactory


class TestGetPeople(TestCase):
    def test_get_labels_and_label_sets(self):
        response = get_people(labels=["foo"], label_sets=["bar"],)
        self.assertEqual(response.errors[0].code, "INVALID_REQUEST")

    def test_get_volunteer_w_label(self):
        context = VolunteerContext()
        label = LabelFactory(allocation=context.allocation)
        response = get_people(labels=[context.conference.conference_slug],
                              roles=["Volunteer"])
        self.assertEqual(response.people[0].label, label.text)

    def test_get_act_w_label(self):
        context = ShowContext()
        act, booking = context.book_act()
        label = LabelFactory(allocation=booking)
        response = get_people(labels=[context.conference.conference_slug],
                              roles=["Performer"])
        target_person = None

        for person in response.people:
            if act.performer.user_object.pk == person.user.pk:
                target_person = person
            else:
                self.assertNotEqual(person.label, label.text)
        self.assertIsNotNone(target_person)
        self.assertEqual(target_person.label, label.text)
