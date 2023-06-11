from django.test import TestCase
from scheduler.idd import get_people
from tests.contexts import (
    ShowContext,
    VolunteerContext,
)


class TestGetPeople(TestCase):
    def test_get_labels_and_label_sets(self):
        response = get_people(labels=["foo"], label_sets=["bar"],)
        self.assertEqual(response.errors[0].code, "INVALID_REQUEST")

    def test_get_volunteer_w_label(self):
        context = VolunteerContext()
        context.allocation.label = "test_get_volunteer_w_label"
        context.allocation.save()
        response = get_people(labels=[context.conference.conference_slug],
                              roles=["Volunteer"])
        self.assertEqual(response.people[0].label, context.allocation.label)

    def test_get_act_w_label(self):
        context = ShowContext()
        act, booking = context.book_act()
        booking.label = "test_get_act_w_label"
        booking.save()
        response = get_people(labels=[context.conference.conference_slug],
                              roles=["Performer"])
        target_person = None

        for person in response.people:
            if act.bio.user_object.pk == person.users[0].pk:
                target_person = person
            else:
                self.assertNotEqual(person.label, booking.label)
        self.assertIsNotNone(target_person)
        self.assertEqual(target_person.label, booking.label)
