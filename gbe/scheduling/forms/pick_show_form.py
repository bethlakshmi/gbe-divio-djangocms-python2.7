from django.forms import (
    ChoiceField,
    Form,
    RadioSelect,
)
from gbe.models import Show
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
            show_pks = Show.objects.filter(
                e_conference=initial['conference']
                ).order_by('e_title').values_list('eventitem_id', flat=True)
            if len(show_pks) > 0:
                response = get_occurrences(foreign_event_ids=show_pks)
                for occurrence in response.occurrences:
                    event = Show.objects.get(
                        eventitem_id=occurrence.foreign_event_id)
                    choices += [
                        (occurrence.pk, "%s - %s" % (
                            event.e_title,
                            occurrence.start_time.strftime(
                                GBE_DATETIME_FORMAT)))]
            choices += [("", "Make New Show")]
            self.fields['show'].choices = choices
