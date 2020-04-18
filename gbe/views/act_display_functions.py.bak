from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.forms import (
    ChoiceField,
)
from gbe.models import (
    Act,
    ActCastingOption,
    UserMessage,
)
from gbetext import (
    default_act_title_conflict,
    act_not_unique,
)
from gbe_forms_text import act_bid_labels


def display_invalid_act(request, data, form, conference, profile, view):
    if [act_not_unique] in form.errors.values():
        conflict_msg = UserMessage.objects.get_or_create(
            view=view,
            code="ACT_TITLE_CONFLICT",
            defaults={
                'summary': "Act Title, User, Conference Conflict",
                'description': default_act_title_conflict})
        conflict = Act.objects.filter(
            b_conference=conference,
            b_title=form.data['theact-b_title'],
            performer__contact=profile).first()
        if conflict.submitted:
            link = reverse(
                'act_view',
                urlconf='gbe.urls',
                args=[conflict.pk]
            )
        else:
            link = reverse(
                'act_edit',
                urlconf='gbe.urls',
                args=[conflict.pk]
            )
        messages.error(
            request, conflict_msg[0].description % (
                link,
                conflict.b_title))
    return render(
        request,
        'gbe/bid.tmpl',
        data
    )


def get_act_form(act, form, header):
    initial = {
        'track_title': act.tech.track_title,
        'track_artist': act.tech.track_artist,
        'act_duration': act.tech.duration
    }
    act_form = form(
        instance=act,
        prefix=header,
        initial=initial)
    act_form.fields['video_choice'] = ChoiceField(
            choices=[(act.video_choice,
                      act.get_video_choice_display())],
            label=act_bid_labels['video_choice'])

    return act_form


def get_act_casting():
    castings = ActCastingOption.objects.all()
    cast_list = []
    for casting in castings:
        value = casting.casting
        if not casting.show_as_special:
            value = ''
        cast_list += [(value, casting.casting)]

    return cast_list
