from django.views import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
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
from gbe_utils.mixins import ProfileRequiredMixin
from gbe.views.functions import make_show_casting_form
from gbe.scheduling.views.functions import (
    shared_groundwork,
    show_general_status,
)
from gbe.models import (
    Act,
    Conference,
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
    act_panel_instr,
    no_scope_error,
    role_commit_map,
    volunteer_panel_instr,
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
    assign_act_perm = ('Producer', 'Stage Manager')
    approve_volunteers = ('Technical Director',
                          'Scheduling Mavens',
                          'Producer',
                          'Stage Manager',
                          'Staff Lead')

    def setup_email_forms(self):
        role_form = SecretRoleInfoForm(
            initial={'conference': [self.conference],
                     'roles': None},
            prefix="email-select")
        event_form = SelectEventForm(
            prefix="event-select",
            initial={'events': [self.occurrence.pk]})

        choices = [self.occurrence.pk, self.occurrence.title]
        event_form['events'].choices = choices
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
            (self.profile, self.occurrence) = groundwork_data
        self.conference = Conference.objects.filter(
            conference_slug__in=self.occurrence.labels)[0]
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
        self.can_assign_act = request.user.has_perm(
            'gbe.assign_act') or validate_perms(request,
                                                self.assign_act_perm,
                                                require=False)
        self.show_scope = []
        if validate_perms(request,
                          self.cross_show_scope,
                          require=False):
            self.show_scope = get_occurrences(
                event_styles=['Show'],
                labels=self.occurrence.labels).occurrences
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
                   'Tech Done',
                   'Act',
                   'Performer',
                   'Role',
                   'Rehearsal',
                   'Music',
                   'Action']
        conference = self.conference

        # Setup act pane
        response = get_people(event_ids=[self.occurrence.pk],
                              roles=["Performer"])
        show_general_status(request, response, self.__class__.__name__)
        for performer in response.people:
            rehearsals = []
            order = -1
            show_role = "NO ROLE"
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
                        item.event.event_style == "Rehearsal Slot"):
                    rehearsals += [item.event]
                elif item.event.event_style == "Show":
                    order = item.commitment.order
                    show_role = item.commitment.role
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
                                                 self.occurrence.pk,
                                                 performer.commitment.role)
            acts += [{
                'act': act,
                'rehearsals': rehearsals,
                'order': order,
                'show_role': show_role,
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
        vol_msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="VOLUNTEER_PANEL_INSTRUCTIONS",
            defaults={
                'summary': "Instructions at top of Volunteer Panel",
                'description': volunteer_panel_instr})
        return {'email_forms': self.setup_email_forms(),
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
                'can_assign_act': self.can_assign_act,
                'change_acts': self.can_change_techinfo,
                'opps': opps,
                'role_commit_map': role_commit_map,
                'visible_roles': roles,
                'act_panel_instructions': UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="ACT_PANEL_INSTRUCTIONS",
                    defaults={
                        'summary': "Instructions at top of Act Panel",
                        'description': act_panel_instr})[0].description,
                'volunteer_panel_instructions': vol_msg[0].description,
                'vol_columns': ['Event',
                                'Area',
                                'Date/Time',
                                'Location',
                                'Max',
                                'Current',
                                'Volunteers']}

    @method_decorator(never_cache, name="post")
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
                # don't need to change users on People here
                person = Person(
                    public_id=act['act'].performer.pk,
                    public_class=act['act'].performer.__class__.__name__,
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

    @method_decorator(never_cache, name="get")
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        return render(request,
                      self.template,
                      self.get_context_data(request))

    def dispatch(self, *args, **kwargs):
        return super(ShowDashboard, self).dispatch(*args, **kwargs)
