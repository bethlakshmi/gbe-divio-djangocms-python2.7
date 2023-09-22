from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    ForeignKey,
    Model,
    PositiveIntegerField,
    TextField,
)
from gbe.models import Profile
from filer.fields.image import FilerImageField


class Bio(Model):
    '''
    Used to be "Performer", and the base for Persona and Troupe.  Refactored
    so that the person booked as part of this bio is in the scheduler, while
    this is used purely for the information *about* that entity.
    '''
    contact = ForeignKey(Profile,
                         on_delete=CASCADE)
    name = CharField(max_length=100)
    label = CharField(max_length=100, blank=True)
    bio = TextField()
    experience = PositiveIntegerField(blank=True, null=True)
    year_started = PositiveIntegerField(null=True)
    awards = TextField(blank=True)
    img = FilerImageField(
        on_delete=CASCADE,
        null=True,
        related_name="image_bio")
    festivals = TextField(blank=True)     # placeholder only
    pronouns = CharField(max_length=128, blank=True)
    multiple_performers = BooleanField(default=False)

    def has_bids(self):
        return (self.is_teaching.count() > 0 or self.acts.count() > 0 or
                self.costume_set.count() > 0)

    def related_bids(self):
        bids = list(self.is_teaching.all()) + list(self.acts.all()) + list(
            self.costume_set.all())
        bids.sort(reverse=True, key=lambda b: b.b_conference.conference_slug)
        return bids

    @property
    def user_object(self):
        return self.contact.user_object

    def __str__(self):
        perf_string = self.name
        if self.label and len(self.label) > 0:
            perf_string = "%s - %s" % (self.name, self.label)
        return perf_string

    class Meta:
        ordering = ['name']
        app_label = "gbe"
        unique_together = [['name', 'label']]
