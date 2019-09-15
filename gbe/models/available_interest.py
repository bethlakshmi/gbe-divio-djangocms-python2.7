from django.db.models import (
    BooleanField,
    CharField,
    Model,
    TextField,
)


class AvailableInterest(Model):
    interest = CharField(
        max_length=128,
        unique=True)
    visible = BooleanField(default=True)
    help_text = TextField(blank=True)

    def __str__(self):
        return self.interest

    class Meta:
        app_label = "gbe"
