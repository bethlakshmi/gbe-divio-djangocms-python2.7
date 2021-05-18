from django.db.models import (
    CASCADE,
    ForeignKey,
)
from gbe.models import (
    Biddable,
    Profile,
)


class Volunteer(Biddable):
    '''
    Represents a conference attendee's participation as a volunteer.
    '''
    profile = ForeignKey(Profile,
                         on_delete=CASCADE,
                         related_name="volunteering")

    def __str__(self):
        return self.profile.display_name

    @property
    def bidder_is_active(self):
        return self.profile.user_object.is_active

    class Meta:
        app_label = "gbe"
