from django.test import TestCase
from scheduler.idd import get_all_container_bookings
from tests.contexts import VolunteerContext


class TestGetAllContainerBookings(TestCase):

    def setUp(self):
        self.context = VolunteerContext()

    def test_get_person_w_label(self):
        self.context.allocation.label = "test_get_person_w_label"
        self.context.allocation.save()
        response = get_all_container_bookings(
            occurrence_ids=[self.context.opp_event.pk])
        self.assertEqual(response.people[0].label,
                         self.context.allocation.label)
