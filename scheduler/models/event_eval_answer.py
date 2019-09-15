from django.db.models import (
    Model,
    ForeignKey,
)
from scheduler.models import (
    EventEvalQuestion,
    Event,
    WorkerItem,
)


class EventEvalAnswer(Model):
    question = ForeignKey(EventEvalQuestion)
    profile = ForeignKey(WorkerItem)
    event = ForeignKey(Event)

    class Meta:
        app_label = "scheduler"
        abstract = True
        unique_together = (('profile', 'event', 'question'),)
