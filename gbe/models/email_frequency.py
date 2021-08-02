from django.db.models import (
    CharField,
    IntegerField,
    Model,
)
from gbetext import day_of_week


class EmailFrequency(Model):
    email_type = CharField(max_length=128)
    weekday = IntegerField(choices=day_of_week)

    class Meta:
        app_label = "gbe"
