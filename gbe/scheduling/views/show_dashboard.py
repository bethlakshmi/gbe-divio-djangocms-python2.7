from django.views import View
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import (
    render,
    get_object_or_404,
)
from gbe.functions import (
    conference_slugs,
    validate_perms,
)
from gbe.views import ProfileRequiredMixin
from gbe.scheduling.views.functions import (
    shared_groundwork,
    show_general_status,
)
from gbe.models import (
    Act,
    GenericEvent,
    Show,
    UserMessage,
)
from scheduler.idd import (
    get_occurrences,
    get_people,
    get_schedule,
)
from gbetext import no_scope_error


class ShowDashboard(ProfileRequiredMixin, View):
    template = 'gbe/scheduling/show_dashboard.tmpl'
    conference = None
    view_perm = ('Scheduling Mavens',
                 'Stage Manager',
                 'Tech Crew',
                 'Technical Director',
                 'Producer')
    schedule_act_perm = ('Scheduling Mavens', 'Stage Manager')
    change_tech_perm = ('Technical Director', 'Producer', 'Stage Manager')
    cross_show_scope = ('Scheduling Mavens', )

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
        self.can_schedule_acts = validate_perms(request,
                                                self.schedule_act_perm,
                                                require=False)
        self.can_change_techinfo = validate_perms(request,
                                                  self.change_tech_perm,
                                                  require=False)
        self.show_scope = []
        if validate_perms(request,
                          self.cross_show_scope,
                          require=False):
            self.show_scope = get_occurrences(
                foreign_event_ids=Show.objects.filter(
                    e_conference=self.item.e_conference).values_list(
                    'eventitem_id',
                    flat=True)).occurrences
        else:
            check_scope = False
            for item in get_schedule(
                    user=self.profile.user_object,
                    roles=self.view_perm).schedule_items:
                self.show_scope += [item.event]
                if item.event == self.occurrence:
                    check_scope = True
            if not check_scope:
                messages.error(request, UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="NO SHOW SCOPE PRIVILEGE",
                    defaults={
                        'summary': "User is accesing show they don't manage",
                        'description': no_scope_error})[0].description)
                error_url = reverse('home', urlconf='gbe.urls')
                return HttpResponseRedirect(error_url)

    def get_context_data(self, request):
        acts = []
        scheduling_link = ''
        columns = ['Order',
                   'Act',
                   'Performer',
                   'Rehearsal',
                   'Music',
                   'Action']
        conference = self.item.e_conference
        response = get_people(foreign_event_ids=[self.item.eventitem_id],
                              roles=["Performer"])
        show_general_status(request, response, "ReviewActTechinfo")
        for performer in response.people:
            rehearsals = []
            order = -1
            act = get_object_or_404(
                Act,
                pk=performer.commitment.class_id)
            sched_response = get_schedule(
                labels=[act.b_conference.conference_slug],
                commitment=act)
            show_general_status(request, sched_response, "ReviewActTechinfo")
            for item in sched_response.schedule_items:
                if item.event not in rehearsals and (
                        GenericEvent.objects.filter(
                            eventitem_id=item.event.eventitem.eventitem_id,
                            type='Rehearsal Slot').exists()):
                    rehearsals += [item.event]
                elif Show.objects.filter(
                        eventitem_id=item.event.eventitem.eventitem_id
                        ).exists():
                    order = item.commitment.order
            acts += [{'act': act, 'rehearsals': rehearsals, 'order': order}]
        if self.can_schedule_acts:
            scheduling_link = reverse(
                'schedule_acts',
                urlconf='gbe.scheduling.urls',
                args=[self.item.pk])

        return {'this_show': self.item,
                'this_occurrence': self.occurrence,
                'acts': acts,
                'columns': columns,
                'other_shows': self.show_scope,
                'conference_slugs': conference_slugs(),
                'conference': conference,
                'scheduling_link': scheduling_link,
                'change_acts': self.can_change_techinfo,
                'return_link': reverse('act_techinfo_review',
                                       urlconf='gbe.reporting.urls',)}

    @never_cache
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        return render(request,
                      self.template,
                      self.get_context_data(request))

    def dispatch(self, *args, **kwargs):
        return super(ShowDashboard, self).dispatch(*args, **kwargs)
