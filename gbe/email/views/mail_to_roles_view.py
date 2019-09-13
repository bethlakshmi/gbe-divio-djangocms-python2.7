from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from gbe.models import (
    Conference,
    Event,
    GenericEvent,
    StaffArea,
    UserMessage,
)
from gbe.email.forms import (
    SelectEventForm,
    SecretRoleInfoForm,
    SelectRoleForm,
)
from scheduler.idd import get_people
from gbe.email.views import MailToFilterView
from gbetext import (
    role_options,
    to_list_empty_msg
)
from gbe_forms_text import (
    all_roles,
    role_option_privs,
    event_collect_choices,
)
from django.forms import (
    ModelMultipleChoiceField,
    MultipleChoiceField,
)
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Q


class MailToRolesView(MailToFilterView):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Producer',
                            'Registrar',
                            'Schedule Mavens',
                            'Staff Lead',
                            'Technical Director',
                            'Volunteer Coordinator',
                            ]
    template = 'gbe/email/mail_to_roles.tmpl'

    def setup_event_queryset(self, is_superuser, priv_list, conferences):
        # build event field based on privs
        event_queryset = None
        if is_superuser or len(
                [i for i in ["Schedule Mavens",
                             "Registrar",
                             "Volunteer Coordinator"] if i in priv_list]) > 0:
            event_queryset = Event.objects.filter(
                e_conference__in=conferences
                ).filter(
                Q(genericevent__type__in=["Special", "Master"],) |
                Q(show__pk__gt=0))
        elif len([i for i in ['Producer',
                              'Technical Director',
                              'Act Coordinator',
                              'Staff Lead'] if i in priv_list]) > 0:
            query = None
            if 'Staff Lead' in priv_list:
                query = Q(genericevent__type__in=["Special"],)
            if len([i for i in ['Producer',
                                'Technical Director',
                                'Act Coordinator'] if i in priv_list]) > 0:
                if query:
                    query = query | Q(show__pk__gt=0)
                else:
                    query = Q(show__pk__gt=0)
            event_queryset = Event.objects.filter(
                    e_conference__in=conferences
                    ).filter(query)
        return event_queryset

    def setup_staff_queryset(self, is_superuser, priv_list, conferences):
        staff_queryset = None
        if is_superuser or len(
                [i for i in ["Schedule Mavens",
                             "Staff Lead",
                             "Registrar",
                             "Volunteer Coordinator"] if i in priv_list]) > 0:
            staff_queryset = StaffArea.objects.filter(
                conference__in=self.select_form.cleaned_data['conference'])

        return staff_queryset

    def setup_event_collect_choices(self,
                                    is_superuser,
                                    priv_list,
                                    conferences):
        event_collect = []
        if is_superuser or len(
                [i for i in ["Schedule Mavens",
                             "Registrar",
                             "Volunteer Coordinator"] if i in priv_list]) > 0:
            return event_collect_choices
        else:
            if "Class Coordinator" in priv_list:
                event_collect += [
                    ("Conference", "All Conference Classes"), ]
            if "Staff Lead" in priv_list:
                event_collect += [
                    ("Volunteer", "All Volunteer Events"), ]
        return event_collect

    def setup_roles(self):
        if not (self.user.user_object.is_superuser or len(
                [i for i in all_roles if i in self.priv_list]) > 0):
            avail_roles = []
            for key, value in role_option_privs.iteritems():
                if key in self.priv_list:
                    for role in value:
                        if role not in avail_roles:
                            avail_roles.append(role)
            self.select_form.fields['roles'].choices = [
                (role, role) for role in sorted(avail_roles)]

    def groundwork(self, request, args, kwargs):
        self.url = reverse('mail_to_roles', urlconf='gbe.email.urls')
        self.specify_event_form = None
        self.priv_list = self.user.privilege_groups
        self.priv_list += self.user.get_roles()
        if 'filter' in request.POST.keys() or 'send' in request.POST.keys(
                ) or 'refine' in request.POST.keys():
            self.select_form = SelectRoleForm(
                request.POST,
                prefix="email-select")
            self.setup_roles()

            if self.select_form.is_valid():
                self.specify_event_form = SelectEventForm(
                    request.POST,
                    prefix="event-select")
                self.event_queryset = self.setup_event_queryset(
                    self.user.user_object.is_superuser,
                    self.priv_list,
                    self.select_form.cleaned_data['conference'])
                self.staff_queryset = self.setup_staff_queryset(
                    self.user.user_object.is_superuser,
                    self.priv_list,
                    self.select_form.cleaned_data['conference'])
                self.event_collect_choices = self.setup_event_collect_choices(
                    self.user.user_object.is_superuser,
                    self.priv_list,
                    self.select_form.cleaned_data['conference'])
                if self.event_queryset:
                    self.specify_event_form.fields[
                        'events'] = ModelMultipleChoiceField(
                        queryset=self.event_queryset,
                        widget=CheckboxSelectMultiple(),
                        required=False)
                if self.staff_queryset:
                    self.specify_event_form.fields[
                        'staff_areas'] = ModelMultipleChoiceField(
                        queryset=self.staff_queryset,
                        widget=CheckboxSelectMultiple(),
                        required=False)
                if len(self.event_collect_choices) > 0:
                    self.specify_event_form.fields[
                        'event_collections'] = MultipleChoiceField(
                        required=False,
                        widget=CheckboxSelectMultiple(),
                        choices=self.event_collect_choices)
        else:
            self.select_form = SelectRoleForm(
                prefix="email-select",
                initial={
                    'conference': Conference.objects.all().values_list(
                        'pk',
                        flat=True),
                    'roles': [r[0] for r in role_options]})
            self.setup_roles()

    def get_select_forms(self):
        context = {"selection_form": self.select_form}
        if self.specify_event_form:
            context['specify_event_form'] = self.specify_event_form
        return context

    def select_form_is_valid(self):
        if self.specify_event_form:
            return self.select_form.is_valid(
                ) and self.specify_event_form.is_valid()
        return self.select_form.is_valid()

    def create_occurrence_limits(self):
        limits = {
            'parent_ids': [],
            'labels': [],
        }
        for event in self.specify_event_form.cleaned_data['events']:
            limits['parent_ids'] += [event.eventitem_id]
        for area in self.specify_event_form.cleaned_data['staff_areas']:
            limits['labels'] += [area.slug]
        for collection in self.specify_event_form.cleaned_data[
                'event_collections']:
            if collection != "Drop-In":
                limits['labels'] += [collection]
            else:
                for dropin in GenericEvent.objects.filter(type="Drop-In"):
                    limits['parent_ids'] += [dropin.eventitem_id]

        if len(limits['parent_ids']) == 0 and len(limits['labels']) == 0:
            limits = None
        return limits

    def get_to_list(self):
        to_list = []
        slugs = []
        people = []
        limits = None
        for conference in self.select_form.cleaned_data['conference']:
            slugs += [conference.conference_slug]
        if self.specify_event_form:
            limits = self.create_occurrence_limits()
        if self.user.user_object.is_superuser or len(
                [i for i in ["Schedule Mavens",
                             "Registrar",
                             "Volunteer Coordinator"] if i in self.priv_list]
                ) > 0:
            if limits:
                if len(limits['parent_ids']) > 0:
                    response = get_people(
                        parent_event_ids=limits['parent_ids'],
                        labels=slugs,
                        roles=self.select_form.cleaned_data['roles'])
                    people += response.people
                if len(limits['labels']) > 0:
                    response = get_people(
                        label_sets=[slugs, limits['labels']],
                        roles=self.select_form.cleaned_data['roles'])
                    people += response.people
            else:
                response = get_people(
                    labels=slugs,
                    roles=self.select_form.cleaned_data['roles'])
                people += response.people
        else:
            if len([i for i in ['Producer',
                                'Technical Director',
                                'Act Coordinator',
                                'Staff Lead'] if i in self.priv_list]) > 0:
                response = None
                if limits:
                    if len(limits['parent_ids']) > 0:
                        response = get_people(
                            parent_event_ids=limits['parent_ids'],
                            labels=slugs,
                            roles=self.select_form.cleaned_data['roles'])
                else:
                    # this should be doable from a values_list, isn't
                    parent_items = []
                    for item in self.event_queryset:
                        parent_items += [item.eventitem_id]
                    response = get_people(
                        parent_event_ids=parent_items,
                        labels=slugs,
                        roles=self.select_form.cleaned_data['roles'])
                if response:
                    people += response.people
            if "Class Coordinator" in self.priv_list:
                if limits is None or "Conference" in limits['labels']:
                    response = get_people(
                        label_sets=[slugs, ["Conference", ]],
                        roles=self.select_form.cleaned_data['roles'])
                    people += response.people
            if "Staff Lead" in self.priv_list:
                if limits:
                    if len(limits['labels']) > 0:
                        response = get_people(
                            label_sets=[slugs, limits['labels']],
                            roles=self.select_form.cleaned_data['roles'])
                else:
                    allowed_labels = ["Volunteer", ]
                    for area in self.staff_queryset:
                        allowed_labels += [area.slug]
                    response = get_people(
                        label_sets=[slugs, allowed_labels],
                        roles=self.select_form.cleaned_data['roles'])
                people += response.people
        for person in people:
            person_contact = (person.user.email,
                              person.user.profile.display_name)
            if person.user.is_active and person_contact not in to_list:
                to_list += [person_contact]
        return sorted(to_list, key=lambda s: s[1].lower())

    def prep_email_form(self, request):
        to_list = self.get_to_list()
        recipient_info = SecretRoleInfoForm(request.POST,
                                            prefix="email-select")
        event_info = SelectEventForm(request.POST,
                                     prefix="event-select")
        return to_list, [recipient_info, event_info]

    def filter_emails(self, request):
        to_list = self.get_to_list()
        if len(to_list) == 0:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NO_RECIPIENTS",
                defaults={
                    'summary': "Email Sent to Bidders",
                    'description': to_list_empty_msg})
            messages.error(
                request,
                user_message[0].description)
            return render(
                request,
                self.template,
                self.get_select_forms())
        email_form = self.setup_email_form(request, to_list)
        recipient_info = SecretRoleInfoForm(request.POST,
                                            prefix="email-select")
        event_info = SelectEventForm(request.POST,
                                     prefix="event-select")
        context = self.get_select_forms()
        context["email_form"] = email_form
        context["recipient_info"] = [recipient_info, event_info]
        return render(
            request,
            self.template,
            context)
