from django.db.models import (
    CASCADE,
    ForeignKey,
)
from gbe.models import (
    Account,
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
    account = ForeignKey(Account,
                         on_delete=CASCADE,
                         null=True)
    class Meta:
        app_label = "gbe"
