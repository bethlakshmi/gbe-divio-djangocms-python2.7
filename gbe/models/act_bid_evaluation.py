from django.db.models import (
    CASCADE,
    Model,
    ForeignKey,
    TextField,
)
from gbe.models import (
    Act,
    Profile,
    ShowVote,
)


class ActBidEvaluation(Model):
    evaluator = ForeignKey(Profile, on_delete=CASCADE)
    primary_vote = ForeignKey(ShowVote,
                              on_delete=CASCADE,
                              related_name="primary_vote",
                              blank=True,
                              null=True)
    secondary_vote = ForeignKey(ShowVote,
                                on_delete=CASCADE,
                                related_name="secondary_vote",
                                blank=True,
                                null=True)
    notes = TextField(blank=True)
    bid = ForeignKey(Act, on_delete=CASCADE)

    class Meta:
        app_label = "gbe"
        verbose_name = "act bid evaluation"
        verbose_name_plural = "act bid evaluations"
