from django.test import TestCase
from scheduler.idd import get_schedule
from tests.contexts import (
    ShowContext,
    ClassContext,
)
from scheduler.models import PeopleAllocation


class TestGetSchedule(TestCase):

    def test_get_teacher_w_label(self):
        context = ClassContext()
        booking = PeopleAllocation.objects.get(
            event=context.sched_event,
            role='Teacher')
        booking.label = 'test_get_teacher_w_label'
        booking.save()
        response = get_schedule(
            user=context.teacher.get_profiles()[0].user_object)
        self.assertEqual(response.schedule_items[0].label, booking.label)

    def test_get_act_w_label(self):
        context = ShowContext()
        act, booking = context.book_act()
        booking.label = "test_get_act_w_label"
        booking.save()
        response = get_schedule(
            user=act.performer.get_profiles()[0].user_object)
        self.assertEqual(response.schedule_items[0].label, booking.label)

    def test_get_class_no_id(self):
        response = get_schedule(public_class="Bio")
        self.assertEqual(response.errors[0].code,
                         "LINKED_CLASS_AND_ID_REQUIRED")

    def test_get_id_no_class(self):
        response = get_schedule(public_id=20)
        self.assertEqual(response.errors[0].code,
                         "LINKED_CLASS_AND_ID_REQUIRED")

    def test_get_user_and_id_and_class(self):
        context = ClassContext()
        response = get_schedule(
            public_id=20,
            public_class="Bio",
            user=context.teacher.contact.user_object)
        self.assertEqual(response.errors[0].code,
                         "USER_AND_LINKED_CLASS_INCOMPATIBLE")
