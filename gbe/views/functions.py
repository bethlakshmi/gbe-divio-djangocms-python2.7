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
from gbe.models import ActCastingOption


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


def get_act_casting():
    castings = ActCastingOption.objects.all()
    cast_list = []
    for casting in castings:
        value = casting.casting
        cast_list += [(value, casting.casting)]

    return cast_list


# used in review flex bid view and the show dashboard, takes a
# base form to play well with the inheritance in bid review
def make_show_casting_form(conference, base_form, start, casting):
    choices = []
    response = get_occurrences(event_styles=['Show'],
                               labels=[conference.conference_slug])
    for occurrence in response.occurrences:
        choices += [(occurrence.pk, str(occurrence))]
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
