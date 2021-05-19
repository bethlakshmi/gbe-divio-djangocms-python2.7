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

    class Meta:
        app_label = "gbe"
