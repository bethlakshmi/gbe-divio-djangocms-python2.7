from django.forms import (
    CharField,
)
from gbe.forms import ParticipantForm
from gbe.models import Profile
from gbe_forms_text import (
    participant_labels,
)


class ProfileAdminForm(ParticipantForm):
    '''
    Form for administratively modifying a Profile
    '''
    purchase_email = CharField(
        required=True,
        label=participant_labels['purchase_email'])

    class Meta:
        model = Profile
        # purchase_email should be display only
        fields = ('first_name',
                  'last_name',
                  'display_name',
                  'email',
                  'purchase_email',
                  'city',
                  'state',
                  'zip_code',
                  'country',
                  'phone',
                  'best_time',
                  'how_heard',
                  )
