from django.db.models import (
    BooleanField,
    DateField,
    ForeignKey,
    Model,
)
from gbe.models import Conference
from django.utils.formats import date_format


class ConferenceDay(Model):
    day = DateField(blank=True)
    conference = ForeignKey(Conference)
    open_to_public = BooleanField(default=True)

    def __unicode__(self):
        return date_format(self.day, "DATE_FORMAT")

    class Meta:
        ordering = ['day']
        verbose_name = "Conference Day"
        verbose_name_plural = "Conference Days"
        app_label = "gbe"
