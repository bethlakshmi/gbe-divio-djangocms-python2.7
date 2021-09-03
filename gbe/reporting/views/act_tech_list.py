from django.views.generic import View
from django.http import HttpResponse
from django.urls import reverse
import csv
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from scheduler.idd import (
    get_people,
    get_schedule,
)
from gbe.scheduling.views.functions import (
    shared_groundwork,
    show_general_status,
)
from django.shortcuts import get_object_or_404
from gbe.models import (
    Act,
    Show,
)


class ActTechList(View):

    view_perm = ('Act Coordinator',
                 'Scheduling Mavens',
                 'Staff Lead',
                 'Stage Manager',
                 'Technical Director',
                 'Producer')

    def groundwork(self, request, args, kwargs):
        groundwork_data = shared_groundwork(
            request,
            kwargs,
            self.view_perm)
        if groundwork_data is None:
            error_url = reverse('home',
                                urlconf='gbe.urls')
            return HttpResponseRedirect(error_url)
        else:
            (self.profile, self.occurrence, self.item) = groundwork_data

    @never_cache
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url

        header = ['Order',
                  'Performer',
                  'Title',
                  'Duration (HH:MM:SS)',
                  'Starting Position',
                  'Prop Setup',
                  'Pronouns',
                  'Read Intro Exactly',
                  'Intro Text',
                  'Costume Colors',
                  'Starting Lights',
                  'Follow Spot',
                  'Wash Color',
                  'Background Color',
                  'Cue for light change',
                  'Lighting at End',
                  'Track Title',
                  'Track Artist',
                  'Mic Options']
        tech_info = []
        response = get_people(foreign_event_ids=[self.item.eventitem_id],
                              roles=["Performer"])
        show_general_status(request, response, self.__class__.__name__)

        for performer in response.people:
            read_exact = "No"
            light_start = "Lights On"
            light_end = "Lights On"
            prop_setup_list = ""
            follow_spot = "OFF"
            wash = "No selection made"
            background = "No selection made"
            cue = "NONE"
            order = -1
            act = get_object_or_404(
                Act,
                pk=performer.commitment.class_id)
            sched_response = get_schedule(
                labels=[act.b_conference.conference_slug],
                commitment=act)
            show_general_status(request,
                                sched_response,
                                self.__class__.__name__)
            for item in sched_response.schedule_items:
                if Show.objects.filter(
                        eventitem_id=item.event.eventitem.eventitem_id
                        ).exists():
                    order = item.commitment.order
            if act.tech.prop_setup:
                for item in act.tech.prop_setup_list:
                    if len(prop_setup_list) == 0:
                        prop_setup_list = item
                    else:
                        prop_setup_list = "%s, %s" % (prop_setup_list, item)
                prop_setup_list = "%s\n%s" % (prop_setup_list,
                                              act.tech.crew_instruct)
            else:
                prop_setup_list = act.tech.crew_instruct
            if act.tech.read_exact:
                read_exact = "Yes"
            if act.tech.start_blackout:
                light_start = "Blackout"
            if act.tech.end_blackout:
                light_end = "Blackout"
            if act.tech.follow_spot_color:
                follow_spot = act.tech.follow_spot_color
            if act.tech.wash_color:
                wash = act.tech.wash_color
            if act.tech.background_color:
                background = act.tech.background_color
            if act.tech.special_lighting_cue:
                cue = act.tech.special_lighting_cue
            if act.tech.confirm_no_music:
                title = "no music"
                artist = ""
            else:
                title = act.tech.track_title
                artist = act.tech.track_artist
            tech_info.append([
                order,
                str(act.performer),
                act.b_title,
                act.tech.duration,
                act.tech.starting_position,
                prop_setup_list,
                act.tech.pronouns,
                read_exact,
                act.tech.introduction_text,
                "Primary: %s\nSecondary: %s" % (act.tech.primary_color,
                                                act.tech.secondary_color),
                light_start,
                follow_spot,
                wash,
                background,
                cue,
                light_end,
                title,
                artist,
                act.tech.mic_choice,
                ])

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s_tech.csv' % (str(self.item))
        writer = csv.writer(response)
        writer.writerow(header)
        for row in tech_info:
            writer.writerow(row)
        return response
