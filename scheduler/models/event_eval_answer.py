from django.db.models import (
    CASCADE,
    Model,
    ForeignKey,
)
from scheduler.models import (
    EventEvalQuestion,
    Event,
)
from django.contrib.auth.models import User


class EventEvalAnswer(Model):
    question = ForeignKey(EventEvalQuestion, on_delete=CASCADE)
    user = ForeignKey(User, on_delete=CASCADE, null=True)
    event = ForeignKey(Event, on_delete=CASCADE)

    class Meta:
        app_label = "scheduler"
        abstract = True
        unique_together = (('user', 'event', 'question'),)
