# View functions for reporting
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from gbe.models import Show
from gbe.functions import (
    conference_slugs,
    validate_perms,
)
from gbe_logging import logger
from django.utils.formats import date_format


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

        if area in ('all', 'stage_mgmt'):
            rehearsals = ""
            for rehearsal in act.get_scheduled_rehearsals():
                rehearsals += date_format(
                    rehearsal.start_time, "DATETIME_FORMAT") + ", "
            tech_row += [
                rehearsals,
             ]

    return (
        header,
        sorted(techinfo, key=lambda row: row[0]))
