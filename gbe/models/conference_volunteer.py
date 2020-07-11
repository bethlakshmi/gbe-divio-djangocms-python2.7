from django.db.models import (
    CASCADE,
    Model,
    ForeignKey,
    BooleanField,
    CharField,
    TextField,
)
from gbe.models import (
    ClassProposal,
    Persona,
    Profile,
)
from gbe_forms_text import conference_participation_types


class ConferenceVolunteer(Model):
    '''
    An individual wishing to participate in the conference as a volunteer
    (fits with the class proposal above)
    '''
    presenter = ForeignKey(Persona,
                           on_delete=CASCADE,
                           related_name='conf_volunteer')
    bid = ForeignKey(ClassProposal, on_delete=CASCADE)
    how_volunteer = CharField(max_length=20,
                              choices=conference_participation_types,
                              default='Any of the Above')
    qualification = TextField(blank='True')
    volunteering = BooleanField(default=True, blank='True')

    @property
    def bid_fields(self):
        return (['volunteering',
                 'presenter',
                 'bid',
                 'how_volunteer',
                 'qualification'],
                ['presenter', 'bid', 'how_volunteer'])

    @property
    def presenter_bid_header(self):
        return (['Interested', 'Presenter', 'Role', 'Qualification'])

    class Meta:
        app_label = "gbe"
