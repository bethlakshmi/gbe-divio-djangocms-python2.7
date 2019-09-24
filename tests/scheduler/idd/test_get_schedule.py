from django.test import TestCase
from scheduler.idd import get_schedule
from tests.contexts import (
    ShowContext,
    ClassContext,
)
from tests.factories.scheduler_factories import LabelFactory
from scheduler.models import ResourceAllocation


class TestGetSchedule(TestCase):

    def test_get_teacher_w_label(self):
        context = ClassContext()
        booking = ResourceAllocation.objects.get(
            event=context.sched_event,
            resource__worker__role='Teacher')
        label = LabelFactory(allocation=booking)
        response = get_schedule(
            user=context.teacher.performer_profile.user_object)
        self.assertEqual(response.schedule_items[0].label.text, label.text)

    def test_get_act_w_label(self):
        context = ShowContext()
        act, booking = context.book_act()
        label = LabelFactory(allocation=booking)
        response = get_schedule(
            user=act.performer.performer_profile.user_object)
        self.assertEqual(response.schedule_items[0].label.text, label.text)
