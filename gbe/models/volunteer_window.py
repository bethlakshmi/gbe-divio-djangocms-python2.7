from datetime import datetime
from django.db.models import (
    ForeignKey,
    Model,
    TimeField,
)
from django.utils.formats import date_format
import pytz
from gbe.models import ConferenceDay


class VolunteerWindow(Model):
    start = TimeField(blank=True)
    end = TimeField(blank=True)
    day = ForeignKey(ConferenceDay)

    def __str__(self):
        return "%s, %s to %s" % (str(self.day),
                                 date_format(self.start, "TIME_FORMAT"),
                                 date_format(self.end, "TIME_FORMAT"))

    def start_timestamp(self):
        return pytz.utc.localize(datetime.combine(self.day.day, self.start))

    def end_timestamp(self):
        return pytz.utc.localize(datetime.combine(self.day.day, self.end))

    @property
    def start_time(self):
        ''' same footprint as scheduler events'''
        return self.start_timestamp()

    @property
    def end_time(self):
        ''' same footprint as scheduler events'''
        return self.end_timestamp()

    class Meta:
        ordering = ['day', 'start']
        verbose_name = "Volunteer Window"
        verbose_name_plural = "Volunteer Windows"
        app_label = "gbe"
