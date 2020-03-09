# View functions for reporting
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache

from gbe.models import (
    Show,
    CueInfo,
)

from gbe.functions import (
    conference_slugs,
    validate_perms,
)
from gbe_logging import logger
from django.utils.formats import date_format
from gbe.reporting.functions import prep_act_tech_info


def build_techinfo(show_id, area='all'):
    '''
    Export a list of act tech info details
    - includes only accepted acts
    - includes incomplete details
    - music sold separately
    area is 'all' for all details available,
        'audio' is for audio details only,
        'lighting' is for only lighting details,
        'stage_mgmt' is for only stage management details (props, mic, etc)
    '''
    # Move this into a function file?  It is not a view.

    show = get_object_or_404(Show, eventitem_id=show_id)
    show_booking = show.scheduler_events.first()
    location = show_booking.location
    acts = show_booking.get_acts(3)

    # build header, segmented in same structure as subclasses
    header = ['Order',
              'Act',
              'Performer',
              'Act Length', ]

    if area in ('all', 'stage_mgmt'):
        header += [
            'Intro Text',
            'Rehearsal Time',
            'Preset Props',
            'Cued Props',
            'Clear Props',
            'Stage Notes',
            'Need Mic',
            'Use Own Mic', ]

    if area in ('all', 'audio'):
        header += [
            'Track',
            'Track Artist',
            'Track Length',
            'No Music',
            'Audio Notes', ]
    if area in ('audio',):
        header += [
            'Need Mic',
            'Use Own Mic', ]

    if area in ('all', 'lighting'):
        cues = CueInfo.objects.filter(techinfo__act__in=acts)
        header += [
            'Act Description',
            'Costume Description',
            'Cue #',
            'Cue off of',
            'Follow spot', ]
        if location.describe == 'Theater':
            header += [
                'Center Spot',
                'Backlight',
                'Cyc Light', ]
        header += [
            'Wash',
            'Sound', ]

    # now build content
    techinfo = []
    for act in acts:
        tech_row = [
            act.order,
            act.b_title,
            ("Person",
             act.performer.contact.user_object.email,
             act.performer),
        ]
        stage_info = act.tech.stage.dump_data
        audio_info = act.tech.audio.dump_data
        tech_row += [stage_info[0], ]

        if area in ('all', 'stage_mgmt'):
            rehearsals = ""
            for rehearsal in act.get_scheduled_rehearsals():
                rehearsals += date_format(
                    rehearsal.start_time, "DATETIME_FORMAT") + ", "
            tech_row += [
                stage_info[1],
                rehearsals,
                stage_info[3],
                stage_info[4],
                stage_info[5],
                stage_info[6],
                audio_info[4],
                audio_info[5],
             ]

        if area in ('all', 'audio'):
            tech_row += [
                ("File", audio_info[2], audio_info[0]),
                audio_info[1],
                audio_info[3],
                audio_info[6],
                audio_info[7],
            ]
        if area in ('audio'):
            tech_row += [
                audio_info[4],
                audio_info[5],
             ]

        if area in ('all', 'lighting'):
            tech_row += act.tech.lighting.dump_data
            cue_sequence = ['List', ]
            cue_off_of = ['List', ]
            follow_spot = ['List', ]
            wash = ['List', ]
            sound_note = ['List', ]
            if location.describe == 'Theater':
                center_spot = ['List', ]
                backlight = ['List', ]
                cyc_color = ['List', ]

            for cue in cues.filter(techinfo__act=act).order_by('cue_sequence'):
                cue_sequence += [cue.cue_sequence]
                cue_off_of += [cue.cue_off_of]
                follow_spot += [cue.follow_spot]
                if location.describe == 'Theater':
                    center_spot += [cue.center_spot]
                    backlight += [cue.backlight]
                    cyc_color += [cue.cyc_color]
                wash += [cue.wash]
                sound_note += [cue.sound_note]

            tech_row += [cue_sequence, cue_off_of, follow_spot]
            if location.describe == 'Theater':
                tech_row += [center_spot, backlight, cyc_color]
            tech_row += [wash, sound_note]

        techinfo.append(tech_row)

    return (
        header,
        sorted(techinfo, key=lambda row: row[0]))
