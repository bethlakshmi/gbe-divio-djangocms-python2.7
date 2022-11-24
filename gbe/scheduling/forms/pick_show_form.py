from django.forms import (
    ChoiceField,
    Form,
    RadioSelect,
)
from scheduler.idd import get_occurrences
from settings import GBE_DATETIME_FORMAT


class PickShowForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    show = ChoiceField(
        choices=[],
        widget=RadioSelect,
        required=False,
        )

    def __init__(self, *args, **kwargs):
        super(PickShowForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            initial = kwargs.pop('initial')
            choices = []

            response = get_occurrences(
                event_styles=["Show"],
                labels=[initial['conference'].conference_slug])
            for occurrence in response.occurrences:
                choices += [
                    (occurrence.pk, "%s - %s" % (
                        occurrence.title,
                        occurrence.start_time.strftime(
                            GBE_DATETIME_FORMAT)))]
            choices += [("", "Make New Show")]
            self.fields['show'].choices = choices
