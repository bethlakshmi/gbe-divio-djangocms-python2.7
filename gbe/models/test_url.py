from django.db.models import (
    CASCADE,
    CharField,
    Model,
    TextField,
)


class TestURL(Model):
    display_name = CharField(max_length=128, unique=True)
    partial_url = CharField(max_length=300, unique=True)
    test_notes = TextField(blank=True)

    def __str__(self):
        return self.display_name

    class Meta:
        app_label = "gbe"
        ordering = ['display_name', ]
