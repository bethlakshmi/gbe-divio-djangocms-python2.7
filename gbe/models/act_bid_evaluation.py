from django.db.models import (
    CASCADE,
    Model,
    ForeignKey,
    TextField,
)
from gbe.models import (
    Profile,
    Act,
)


class ActBidEvaluation(Model):
    evaluator = ForeignKey(Profile, on_delete=CASCADE, null=True)
    notes = TextField(blank=True)
    bid = ForeignKey(Act, on_delete=CASCADE)

    class Meta:
        app_label = "gbe"
        verbose_name = "act bid evaluation"
        verbose_name_plural = "act bid evaluations"
