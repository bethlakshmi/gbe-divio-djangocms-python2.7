from django.db.models import (
    CASCADE,
    ForeignKey,
)
from gbe.models import (
    Account,
    Biddable,
)


class Volunteer(Biddable):
    '''
    Represents a conference attendee's participation as a volunteer.
    '''
    account = ForeignKey(Account,
                         on_delete=CASCADE,
                         null=True)
    class Meta:
        app_label = "gbe"
