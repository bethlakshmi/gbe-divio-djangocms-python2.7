from gbe.forms import ParticipantForm
from django.forms import (
    ChoiceField,
    MultipleChoiceField,
)
from gbe_forms_text import (
    how_heard_options,
    participant_labels,
)
from gbetext import (
    act_casting_label,
    states_options,
)
from scheduler.idd import get_occurrences
from gbe.models import Show
from gbe.views.act_display_functions import get_act_casting


def get_participant_form(profile, prefix='Contact Info'):
    participantform = ParticipantForm(
        instance=profile,
        initial={'email': profile.user_object.email,
                 'first_name': profile.user_object.first_name,
                 'last_name': profile.user_object.last_name},
        prefix=prefix)
    if profile.state:
        participantform.fields['state'] = MultipleChoiceField(
            choices=[(profile.state,
                      dict(states_options)[profile.state])],)
    else:
        participantform.fields['state'] = MultipleChoiceField(
            choices=[('--------', 'No State Chosen')],)
    how_heard_selected = []
    for option in how_heard_options:
        if option[0] in profile.how_heard:
            how_heard_selected += [option]
    if len(how_heard_selected) == 0:
        how_heard_selected = [('', ''), ]
    participantform.fields['how_heard'] = MultipleChoiceField(
        choices=how_heard_selected,
        required=False,
        label=participant_labels['how_heard'])
    return participantform


# used in review flex bid view and the show dashboard, takes a
# base form to play well with the inheritance in bid review
def make_show_casting_form(conference, base_form, start, casting):
    choices = []
    response = get_occurrences(
        foreign_event_ids=Show.objects.filter(
            e_conference=conference).values_list('eventitem_id', flat=True))
    for occurrence in response.occurrences:
        choices += [(occurrence.eventitem.pk, str(occurrence))]
    base_form.fields['show'] = ChoiceField(
        choices=choices,
        label='Pick a Show',
        initial=start)
    base_form.fields['casting'] = ChoiceField(
        choices=get_act_casting(),
        required=False,
        label=act_casting_label,
        initial=casting)
    return base_form
