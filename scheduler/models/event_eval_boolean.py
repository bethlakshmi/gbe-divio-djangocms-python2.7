from django.db.models import BooleanField
from scheduler.models import EventEvalAnswer


class EventEvalBoolean(EventEvalAnswer):
    answer = BooleanField()
