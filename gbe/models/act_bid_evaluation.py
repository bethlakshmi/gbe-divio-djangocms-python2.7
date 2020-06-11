from django.db.models import (
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
    evaluator = ForeignKey(Profile)
    primary_vote = ForeignKey(ShowVote,
                              related_name="primary_vote",
                              blank=True,
                              null=True)
    secondary_vote = ForeignKey(ShowVote,
                                related_name="secondary_vote",
                                blank=True,
                                null=True)
    notes = TextField(blank=True)
    bid = ForeignKey(Act)

    class Meta:
        app_label = "gbe"
        verbose_name = "act bid evaluation"
        verbose_name_plural = "act bid evaluations"
