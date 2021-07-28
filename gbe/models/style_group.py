from django.db.models import (
    CASCADE,
    CharField,
    IntegerField,
    ManyToManyField,
    Model,
    TextField,
)
from gbe.models import TestURL


class StyleGroup(Model):
    name = CharField(max_length=128, unique=True)
    test_urls = ManyToManyField(TestURL, blank=True)
    test_notes = TextField(blank=True)
    order = IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        app_label = "gbe"
        ordering = ['name', ]
