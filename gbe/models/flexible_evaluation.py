from django.db.models import (
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
    Biddable,
    EvaluationCategory,
    Profile,
)


class FlexibleEvaluation(Model):
    evaluator = ForeignKey(Profile)
    bid = ForeignKey(Biddable)
    ranking = IntegerField(validators=[MinValueValidator(-1),
                                       MaxValueValidator(5)],
                           blank=True)
    category = ForeignKey(EvaluationCategory)

    class Meta:
        app_label = "gbe"
        unique_together = (("bid", "evaluator", "category"),)
