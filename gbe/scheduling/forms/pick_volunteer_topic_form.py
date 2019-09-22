from django.forms import (
    ChoiceField,
    Form,
    RadioSelect,
)
from gbe.models import (
    Event,
    StaffArea,
)
from scheduler.idd import get_occurrences
from settings import GBE_DATETIME_FORMAT


class PickVolunteerTopicForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    volunteer_topic = ChoiceField(
        choices=[],
        widget=RadioSelect,
        required=False,
        )

    def __init__(self, *args, **kwargs):
        super(PickVolunteerTopicForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'conference' in kwargs['initial']:
            initial = kwargs.pop('initial')
            complete_choices = []
            event_choices = {
                'Show': [],
                'Special': [],
            }
            staff_choices = []

            response = get_occurrences(labels=[
                initial['conference'].conference_slug,
                "General"])
            for item in response.occurrences:
                event = Event.objects.get_subclass(
                    eventitem_id=item.foreign_event_id)
                if event.event_type in event_choices.keys():
                    event_choices[event.event_type] += [
                        (item.pk, "%s - %s" % (
                            event.e_title,
                            item.start_time.strftime(GBE_DATETIME_FORMAT)))]
            if len(event_choices['Show']) > 0:
                complete_choices += [('Shows', event_choices['Show'])]
            if len(event_choices['Special']) > 0:
                complete_choices += [('Special Events',
                                      event_choices['Special'])]
            for item in StaffArea.objects.filter(
                    conference=initial['conference']):
                staff_choices += [("staff_%d" % item.pk,
                                   item.title)]
            if len(staff_choices) > 0:
                complete_choices += [('Staff Areas', staff_choices)]
            complete_choices += [(
                'Standalone',
                [("", "Make a Volunteer Opportunity with no topic"), ])]
            self.fields['volunteer_topic'].choices = complete_choices
