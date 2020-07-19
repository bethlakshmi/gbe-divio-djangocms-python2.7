from django.db.models import (
    CASCADE,
    Model,
    ForeignKey,
)
from scheduler.models import (
    EventEvalQuestion,
    Event,
    WorkerItem,
)


class EventEvalAnswer(Model):
    question = ForeignKey(EventEvalQuestion, on_delete=CASCADE)
    profile = ForeignKey(WorkerItem, on_delete=CASCADE)
    event = ForeignKey(Event, on_delete=CASCADE)

    class Meta:
        app_label = "scheduler"
        abstract = True
        unique_together = (('profile', 'event', 'question'),)
