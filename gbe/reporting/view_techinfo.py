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
from expo.gbe_logging import logger
from expo.settings import DATETIME_FORMAT
from django.utils.formats import date_format
from gbe.reporting.functions import prep_act_tech_info


@never_cache
def view_techinfo(request):
    '''
    Show the list of act tech info for all acts in a given show for a given
    tech area.
    export specifies the type of export, csv or view.  area is the tech area
    of the information being exported, audio, lighting, stage_mgmt, or all.
    '''

    validate_perms(request, ('Tech Crew',))
    area = request.GET.get('area', 'all')
    show_id = request.GET.get('show_id', None)
    area = request.GET.get('area', 'all')
    show, acts, conference, scheduling_link = prep_act_tech_info(
        request, show_id)

    if show_id:
        logger.info(area+', '+show_id)
        header, techinfo = build_techinfo(show_id, area=area)
        logger.info(techinfo)
        logger.info(header)
    else:
        logger.info(area)
        header = None
        techinfo = None

    return render(request,
                  'gbe/report/view_techinfo.tmpl',
                  {'this_show': show,
                   'area': area,
                   'area_options': ['all', 'audio', 'stage_mgmt', 'lighting'],
                   'all_shows': Show.objects.filter(
                       e_conference=conference),
                   'techinfo': techinfo,
                   'header': header,
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'scheduling_link': scheduling_link,
                   'return_link': reverse('view_techinfo',
                                          urlconf='gbe.reporting.urls',)})


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
