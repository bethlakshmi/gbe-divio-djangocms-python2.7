from gbe.forms import ParticipantForm
from django.forms import MultipleChoiceField
from gbe_forms_text import (
    how_heard_options,
    participant_labels,
)
from gbetext import (
    states_options,
)


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
