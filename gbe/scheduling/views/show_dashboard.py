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
from django.forms import (
    ChoiceField,
    Form,
    HiddenInput
)
from gbe.functions import (
    conference_slugs,
    validate_perms,
)
from gbe.views import ProfileRequiredMixin
from gbe.views.functions import make_show_casting_form
from gbe.scheduling.views.functions import (
    shared_groundwork,
    show_general_status,
)
from gbe.models import (
    Act,
    GenericEvent,
    Show,
    StaffArea,
    UserMessage,
)
from gbe.scheduling.forms import ActScheduleBasics
from gbe.email.forms import (
    SecretRoleInfoForm,
    SelectEventForm,
)
from scheduler.idd import (
    get_occurrences,
    get_people,
    get_schedule,
    set_person,
)
from gbetext import (
    act_order_form_invalid,
    act_order_submit_success,
    no_scope_error,
    role_commit_map,
)
from scheduler.data_transfer import (
    Commitment,
    Person,
)


class ShowDashboard(ProfileRequiredMixin, View):
    template = 'gbe/scheduling/show_dashboard.tmpl'
    conference = None
    view_perm = ('Act Coordinator',
                 'Scheduling Mavens',
                 'Staff Lead',
                 'Stage Manager',
                 'Technical Director',
                 'Producer')
    schedule_act_perm = ('Scheduling Mavens', 'Producer', 'Stage Manager')
    change_tech_perm = ('Technical Director',
                        'Producer',
                        'Stage Manager',
                        'Staff Lead')
    cross_show_scope = ('Scheduling Mavens', 'Act Coordinator', 'Staff Lead')
    rebook_perm = ('Producer', 'Act Coordinator')
    approve_volunteers = ('Technical Director',
                          'Scheduling Mavens',
                          'Producer',
                          'Stage Manager',
                          'Staff Lead')

    def setup_email_forms(self):
        role_form = SecretRoleInfoForm(
            initial={'conference': [self.item.e_conference],
                     'roles': None},
            prefix="email-select")
        event_form = SelectEventForm(
            prefix="event-select",
            initial={'events': [self.item]})
        event_form['events'].queryset = Show.objects.filter(pk=self.item.pk)
        event_form['staff_areas'].queryset = None
        event_form['event_collections'].queryset = None
        return [role_form, event_form]

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
        self.can_rebook = validate_perms(request,
                                         self.rebook_perm,
                                         require=False)
        self.can_approve_vol = validate_perms(request,
                                              self.approve_volunteers,
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
                    code="NO_SHOW_SCOPE_PRIVILEGE",
                    defaults={
                        'summary': "User is accesing show they don't manage",
                        'description': no_scope_error})[0].description)
                error_url = reverse('home', urlconf='gbe.urls')
                return HttpResponseRedirect(error_url)

    def get_context_data(self, request):
        acts = []
        all_valid = True
        scheduling_link = ''
        columns = ['Order',
                   'Act',
                   'Performer',
                   'Rehearsal',
                   'Music',
                   'Action']
        conference = self.item.e_conference

        # Setup act pane
        response = get_people(foreign_event_ids=[self.item.eventitem_id],
                              roles=["Performer"])
        show_general_status(request, response, self.__class__.__name__)
        for performer in response.people:
            rehearsals = []
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
                if item.event not in rehearsals and (
                        GenericEvent.objects.filter(
                            eventitem_id=item.event.eventitem.eventitem_id,
                            type='Rehearsal Slot').exists()):
                    rehearsals += [item.event]
                elif Show.objects.filter(
                        eventitem_id=item.event.eventitem.eventitem_id
                        ).exists():
                    order = item.commitment.order
            if request.POST:
                form = ActScheduleBasics(
                    request.POST,
                    prefix=performer.booking_id)
                all_valid = all_valid and form.is_valid()
            else:
                form = ActScheduleBasics(
                    prefix=performer.booking_id,
                    initial={'order': performer.commitment.order})
            rebook_form = Form()
            rebook_form.fields['accepted'] = ChoiceField(
                choices=((3, 3), ),
                initial=3,
                widget=HiddenInput())
            rebook_form = make_show_casting_form(conference,
                                                 rebook_form,
                                                 self.item.eventitem_id,
                                                 performer.commitment.role)
            acts += [{
                'act': act,
                'rehearsals': rehearsals,
                'order': order,
                'rebook_form': rebook_form,
                'form': form}]

        # Setup Volunteer pane
        opps = []
        roles = []
        for role, commit in list(role_commit_map.items()):
            if commit[0] > 0 and commit[0] < 4:
                roles += [role]
        opps_response = get_occurrences(
            labels=[conference.conference_slug, "Volunteer"],
            parent_event_id=self.occurrence.pk)

        if opps_response:
            show_general_status(request,
                                opps_response,
                                self.__class__.__name__)
            for opp in opps_response.occurrences:
                item = {
                    'event': opp,
                    'areas': [],
                }
                for area in StaffArea.objects.filter(slug__in=opp.labels,
                                                     conference=conference):
                    item['areas'] += [area]
                opps += [item]
        return {'this_show': self.item,
                'email_forms': self.setup_email_forms(),
                'this_occurrence': self.occurrence,
                'acts': acts,
                'all_valid': all_valid,
                'columns': columns,
                'other_shows': self.show_scope,
                'conference_slugs': conference_slugs(),
                'conference': conference,
                'can_schedule': self.can_schedule_acts,
                'can_rebook': self.can_rebook,
                'can_approve_vol': self.can_approve_vol,
                'change_acts': self.can_change_techinfo,
                'opps': opps,
                'role_commit_map': role_commit_map,
                'visible_roles': roles,
                'vol_columns': ['Event',
                                'Area',
                                'Date/Time',
                                'Location',
                                'Max',
                                'Current',
                                'Volunteers']}

    @never_cache
    def post(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        data = self.get_context_data(request)
        if not data['all_valid']:
            messages.error(request, UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="ACT_SCHED_ERROR",
                defaults={
                    'summary': "Act Order Forms not valid",
                    'description': act_order_form_invalid})[0].description)
            data['open_panel'] = 'act'
        else:
            for act in data['acts']:
                person = Person(public_id=act['act'].performer.pk,
                                booking_id=act['form'].prefix,
                                role="Performer",
                                commitment=Commitment(
                                    decorator_class=act['act'],
                                    order=act['form'].cleaned_data['order']))
                response = set_person(person=person,
                                      occurrence_id=self.occurrence.pk)
                # we don't care about overbook warnings on this case
                response.warnings = []
                show_general_status(request,
                                    response,
                                    self.__class__.__name__)
            # I can't think of a reason the set_person could fail that isn't
            # already ruled out by how the request is constructed.
            messages.success(request, UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="ACT_SCHED_SUCCESS",
                defaults={
                    'summary': "Order of Acts was updated",
                    'description': act_order_submit_success})[0].description)

        return render(request, self.template, data)

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
