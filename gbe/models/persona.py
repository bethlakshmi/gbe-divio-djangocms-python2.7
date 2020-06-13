from django.db.models import ForeignKey
from gbe.models import (
    Performer,
    Profile,
)


class Persona (Performer):
    '''
    The public persona of one person who performs or teaches.
    May be aggregated into a group or a troupe,
    or perform solo, or both. A single person might conceivably maintain two
    distinct performance identities and therefore have multiple
    Persona objects associated with their profile. For example, a
    person who dances under one name and teaches under another would
    have multiple Personae.
    performer_profile is the profile of the user who dons this persona.
    '''
    performer_profile = ForeignKey(Profile, related_name="personae")

    '''
    Returns the single profile associated with this persona
    '''
    def get_profiles(self):
        return [self.performer_profile]

    class Meta:
        verbose_name_plural = 'personae'
        app_label = "gbe"
