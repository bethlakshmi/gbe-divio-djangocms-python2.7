from django.db.models import (
    Model,
    BooleanField,
    CharField,
    IntegerField,
    TextField,
)
from gbetext import answer_types


class EventEvalQuestion(Model):
    question = CharField(blank=False, max_length=200)
    visible = BooleanField(default=True)
    help_text = TextField(blank=True, max_length=500)
    order = IntegerField()
    answer_type = CharField(choices=(answer_types),
                            max_length=20)

    def __str__(self):
        return "%d - %s" % (self.order, self.question)

    class Meta:
        app_label = "scheduler"
        unique_together = (
            ('question', ),
            ('order', ),)
        ordering = ["order", ]
