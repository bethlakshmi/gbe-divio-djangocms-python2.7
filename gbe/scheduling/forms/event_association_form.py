from django.forms import (
    ChoiceField,
    ModelChoiceField,
    Form,
)
from gbe.models import (
    Conference,
    StaffArea,
)
from scheduler.idd import get_occurrences
from django.db.models.fields import BLANK_CHOICE_DASH
from settings import GBE_DATETIME_FORMAT


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

    def __init__(self, *args, **kwargs):
        event_type = None
        choices = []
        events = None
        super(EventAssociationForm, self).__init__(*args, **kwargs)
        response = get_occurrences(
            event_styles=["Show", "Special"],
            labels=Conference.all_slugs(current=True))
        if response.occurrences:
            for occurrence in response.occurrences:
                choices += [(occurrence.pk, "%s - %s" % (
                    str(occurrence),
                    occurrence.start_time.strftime(GBE_DATETIME_FORMAT)))]
        self.fields['parent_event'].choices = BLANK_CHOICE_DASH + choices
