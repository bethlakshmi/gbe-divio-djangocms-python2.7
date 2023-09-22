from django.urls import reverse_lazy
from django.forms import (
    ChoiceField,
    ModelChoiceField,
    Form,
)
from gbe.models import (
    Conference,
    StaffArea,
)
from scheduler.idd import (
    get_event_list,
    get_occurrences,
)
from django.db.models.fields import BLANK_CHOICE_DASH
from settings import GBE_DATETIME_FORMAT
from dal import (
    autocomplete,
    forward
)


class EventAssociationForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    parent_event = ChoiceField(choices=[],
                               required=False)

    staff_area = ModelChoiceField(
        queryset=StaffArea.objects.exclude(conference__status="completed"),
        required=False)

    peer_event = autocomplete.Select2ListChoiceField(
        choice_list=get_event_list(),
        required=False,
        widget=autocomplete.ListSelect2(
            url=reverse_lazy('volunteer-autocomplete',
                             urlconf="gbe.scheduling.urls"),
            attrs={'data-minimum-input-length': 3}))

    def __init__(self, *args, **kwargs):
        choices = []
        self.conference = None
        super(EventAssociationForm, self).__init__(*args, **kwargs)

        label_set = [Conference.all_slugs(current=True)]
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            self.conference = kwargs['initial']['conference']
            label_set = [[self.conference.conference_slug]]
            self.fields['peer_event'].widget.forward = (
                forward.Const(self.conference.conference_slug, 'label'), )
            self.fields['peer_event'].choice_list = get_event_list(
                label=self.conference.conference_slug)

        response = get_occurrences(
            event_styles=["Show", "Special"],
            label_sets=label_set)
        if response.occurrences:
            for occurrence in response.occurrences:
                title = str(occurrence)
                if len(title) > 30:
                    title = title[:27] + "..."

                choices += [(occurrence.pk, "%s - %s" % (
                    title,
                    occurrence.start_time.strftime(GBE_DATETIME_FORMAT)))]
        self.fields['parent_event'].choices = BLANK_CHOICE_DASH + choices
