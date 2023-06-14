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
from gbe.models import Act


class PerformerSlidesList(View):

    view_perm = ['Act Coordinator',
                 'Scheduling Mavens',
                 'Slide Helper',
                 'Staff Lead',
                 'Stage Manager',
                 'Technical Director',
                 'Producer']

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
            (self.profile, self.occurrence) = groundwork_data

    @never_cache
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url

        header = ['Order',
                  'Performer',
                  'Link1',
                  'Link2',
                  'Link3',
                  ]
        slide_info = []
        response = get_people(event_ids=[self.occurrence.pk],
                              roles=["Performer"])
        show_general_status(request, response, self.__class__.__name__)

        for performer in response.people:
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
                if item.event.event_style == "Show":
                    order = item.commitment.order
            url_set = []
            for link in act.performer.links.filter(order__lt=4):
                if not link.social_network == "Website":
                    url_set += ["%s - %s" % (link.social_network,
                                             link.username)]
                else:
                    url_set += [link.get_url()]
            for i in range(len(url_set), 3):
                url_set += ['']
            slide_info.append([
                order,
                str(act.performer),
                url_set[0],
                url_set[1],
                url_set[2],
                ])
        slide_info.sort()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; filename=%s_perf_urls.csv') % (
            str(self.occurrence))
        writer = csv.writer(response)
        writer.writerow(header)
        for row in slide_info:
            writer.writerow(row)
        return response
