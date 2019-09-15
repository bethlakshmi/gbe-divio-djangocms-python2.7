from django.db.models import TextField
from scheduler.models import EventEvalAnswer


class EventEvalComment(EventEvalAnswer):
    answer = TextField(blank=True, max_length=500)
