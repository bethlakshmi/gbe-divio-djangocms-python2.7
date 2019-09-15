from django.db.models import (
    IntegerField,
)
from scheduler.models import EventEvalAnswer
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from gbetext import new_grade_options


class EventEvalGrade(EventEvalAnswer):
    answer = IntegerField(choices=new_grade_options,
                          blank=True,
                          null=True,
                          validators=[MinValueValidator(-1),
                                      MaxValueValidator(5)])
