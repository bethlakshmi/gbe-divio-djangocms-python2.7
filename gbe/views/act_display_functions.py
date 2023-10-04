from django.forms import (
    ChoiceField,
)
from gbetext import (
    act_shows_options,
    old_act_shows_options,
)
from gbe_forms_text import act_bid_labels


def get_act_form(act, form, header):
    initial = {
        'track_title': act.tech.track_title,
        'track_artist': act.tech.track_artist,
        'act_duration': act.tech.duration,
        'first_name': act.bio.contact.user_object.first_name,
        'last_name': act.bio.contact.user_object.last_name,
        'phone': act.bio.contact.phone,
    }
    act_form = form(
        instance=act,
        prefix=header,
        initial=initial)
    act_form.fields['video_choice'] = ChoiceField(
            choices=[(act.video_choice,
                      act.get_video_choice_display())],
            label=act_bid_labels['video_choice'])
    act_form.fields['shows_preferences'].choices = old_act_shows_options + \
        act_shows_options
    return act_form
