from django.db.models import (
    CASCADE,
    ForeignKey,
)
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
    performer_profile = ForeignKey(Profile,
                                   on_delete=CASCADE,
                                   related_name="personae")

    '''
    Returns the single profile associated with this persona
    '''
    def get_profiles(self):
        return [self.performer_profile]

    def has_bids(self):
        return (self.is_teaching.count() > 0 or self.acts.count() > 0 or 
                self.costume_set.count() > 0)

    class Meta:
        verbose_name_plural = 'personae'
        app_label = "gbe"
