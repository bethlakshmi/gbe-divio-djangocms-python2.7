from django.db.models import (
    CASCADE,
    CharField,
    Model,
    ForeignKey,
    IntegerField,
)
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from gbe.models import (
    Account,
    Biddable,
    EvaluationCategory,
    Profile,
)


class FlexibleEvaluation(Model):
    evaluator = ForeignKey(Profile, on_delete=CASCADE)
    evaluator_acct = ForeignKey(Account, on_delete=CASCADE, null=True)
    bid = ForeignKey(Biddable, on_delete=CASCADE)
    ranking = IntegerField(validators=[MinValueValidator(-1),
                                       MaxValueValidator(5)],
                           blank=True)
    category = ForeignKey(EvaluationCategory, on_delete=CASCADE)

    class Meta:
        app_label = "gbe"
        unique_together = (("bid", "evaluator", "category"),)
