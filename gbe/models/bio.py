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
from scheduler.idd import get_bookable_people


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

    def get_profiles(self):
        '''
        Gets all of the people performing in the act
        '''
        profiles = []
        response = get_bookable_people(self.pk, self.__class__.__name__)
        if len(response.people) > 0:
            profiles = Profile.objects.filter(
                user_object__in=response.people[0].users)
        elif not self.multiple_performers:
            profiles = [self.contact]

        return profiles

    def has_bids(self):
        return (self.is_teaching.count() > 0 or self.acts.count() > 0 or
                self.costume_set.count() > 0)

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
