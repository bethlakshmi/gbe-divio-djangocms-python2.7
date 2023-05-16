from django.db.models import ManyToManyField
from gbe.models import (
    Performer,
    Persona,
)


class Troupe(Performer):
    '''
    Two or more performers working together as an established entity. A troupe
    connotes an entity with a stable membership, a history, and hopefully a
    future. This suggests that a troupe should have some sort of legal
    existence, though this is not required for GBE. Further specification
    welcomed.
    '''
    membership = ManyToManyField(Persona,
                                 related_name='troupes')

    '''
        Gets all of the people performing in the act.
        For troupe, that is every profile of every member in membership
    '''
    def get_profiles(self):
        profiles = []
        for member in Persona.objects.filter(troupes=self):
            profiles += member.get_profiles()
        return profiles

    def has_bids(self):
        return self.acts.count() > 0

    class Meta:
        app_label = "gbe"
