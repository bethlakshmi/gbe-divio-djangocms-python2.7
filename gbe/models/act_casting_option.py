from django.db.models import (
    Model,
    BooleanField,
    IntegerField,
    CharField,
)


class ActCastingOption(Model):
    casting = CharField(max_length=50, unique=True)
    show_as_special = BooleanField(default=True)
    display_order = IntegerField(unique=True)

    class Meta:
        app_label = "gbe"
        ordering = ["display_order", ]
