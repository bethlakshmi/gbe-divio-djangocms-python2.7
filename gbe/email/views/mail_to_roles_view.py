from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from gbe.models import (
    Bio,
    Conference,
    StaffArea,
    UserMessage,
)
from gbe.email.forms import (
    SelectEventForm,
    SecretRoleInfoForm,
    SelectRoleForm,
)
from scheduler.idd import (
    get_occurrences,
    get_people,
)
from gbe.email.views import MailToFilterView
from gbetext import to_list_empty_msg
from gbe_forms_text import (
    all_roles,
    role_option_privs,
    event_collect_choices,
)
from django.forms import (
    ModelMultipleChoiceField,
    MultipleChoiceField,
    MultipleHiddenInput,
)
from django.forms.widgets import CheckboxSelectMultiple
from django.db.models import Q


class MailToRolesView(MailToFilterView):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Producer',
                            'Registrar',
                            'Scheduling Mavens',
                            'Staff Lead',
                            'Stage Manager',
                            'Technical Director',
                            'Volunteer Coordinator',
                            ]
    template = 'gbe/email/mail_to_roles.tmpl'
    email_type = 'role_notifications'

    def setup_event_choices(self, is_superuser, priv_list):
        # build event field based on privs
        permitted_styles = []
        choices = []
        if is_superuser or len(
                [i for i in ["Scheduling Mavens",
                             "Registrar",
                             "Volunteer Coordinator",
                             "Staff Lead"] if i in priv_list]) > 0:
            permitted_styles = ["Special", "Master", "Show"]
        elif len([i for i in ['Producer',
                              'Technical Director',
                              'Stage Manager',
                              'Act Coordinator'] if i in priv_list]) > 0:
            permitted_styles = ["Show"]

        if len(permitted_styles) > 0:
            response = get_occurrences(
                event_styles=permitted_styles,
                label_sets=[self.slugs])
            for occurrence in response.occurrences.order_by('title'):
                choices += [(occurrence.pk, occurrence.title)]
        return choices

    def setup_staff_queryset(self, is_superuser, priv_list, conferences):
        staff_queryset = None
        if is_superuser or len(
                [i for i in ["Scheduling Mavens",
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
                [i for i in ["Scheduling Mavens",
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
            for key, value in role_option_privs.items():
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
        if 'filter' in list(request.POST.keys()) or 'send' in list(
                request.POST.keys()) or 'refine' in list(request.POST.keys()):
            self.select_form = SelectRoleForm(
                request.POST,
                prefix="email-select")
            self.setup_roles()

            if self.select_form.is_valid():
                self.slugs = []
                for conference in self.select_form.cleaned_data['conference']:
                    self.slugs += [conference.conference_slug]
                self.specify_event_form = SelectEventForm(
                    request.POST,
                    prefix="event-select")
                self.event_choices = self.setup_event_choices(
                    self.user.user_object.is_superuser,
                    self.priv_list)
                self.staff_queryset = self.setup_staff_queryset(
                    self.user.user_object.is_superuser,
                    self.priv_list,
                    self.select_form.cleaned_data['conference'])
                self.event_collect_choices = self.setup_event_collect_choices(
                    self.user.user_object.is_superuser,
                    self.priv_list,
                    self.select_form.cleaned_data['conference'])
                if len(self.event_choices) > 0:
                    self.specify_event_form.fields[
                        'events'] = MultipleChoiceField(
                        choices=self.event_choices,
                        widget=CheckboxSelectMultiple(
                            attrs={'class': 'form-check-input'}),
                        required=False)
                if self.staff_queryset:
                    self.specify_event_form.fields[
                        'staff_areas'] = ModelMultipleChoiceField(
                        queryset=self.staff_queryset,
                        widget=CheckboxSelectMultiple(
                            attrs={'class': 'form-check-input'}),
                        required=False)
                if len(self.event_collect_choices) > 0:
                    self.specify_event_form.fields[
                        'event_collections'] = MultipleChoiceField(
                        required=False,
                        widget=CheckboxSelectMultiple(
                            attrs={'class': 'form-check-input'}),
                        choices=self.event_collect_choices)
        else:
            self.select_form = SelectRoleForm(
                prefix="email-select")
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
            limits['parent_ids'] += [event]
        for area in self.specify_event_form.cleaned_data['staff_areas']:
            limits['labels'] += [area.slug]
        for collection in self.specify_event_form.cleaned_data[
                'event_collections']:
            if collection != "Drop-In":
                limits['labels'] += [collection]
            else:
                for dropin in get_occurrences(event_styles=['Drop-In'],
                                              labels=self.slugs).occurrences:
                    limits['parent_ids'] += [dropin.pk]

        if len(limits['parent_ids']) == 0 and len(limits['labels']) == 0:
            limits = None
        return limits

    def get_to_list(self):
        to_list = []
        people = []
        limits = None

        if self.specify_event_form:
            limits = self.create_occurrence_limits()
        if self.user.user_object.is_superuser or len(
                [i for i in ["Scheduling Mavens",
                             "Registrar",
                             "Volunteer Coordinator"] if i in self.priv_list]
                ) > 0:
            if limits:
                if len(limits['parent_ids']) > 0:
                    response = get_people(
                        parent_event_ids=limits['parent_ids'],
                        labels=self.slugs,
                        roles=self.select_form.cleaned_data['roles'])
                    people += response.people
                if len(limits['labels']) > 0:
                    response = get_people(
                        label_sets=[self.slugs, limits['labels']],
                        roles=self.select_form.cleaned_data['roles'])
                    people += response.people
            else:
                response = get_people(
                    labels=self.slugs,
                    roles=self.select_form.cleaned_data['roles'])
                people += response.people
        else:
            if len([i for i in ['Producer',
                                'Technical Director',
                                'Stage Manager',
                                'Act Coordinator',
                                'Staff Lead'] if i in self.priv_list]) > 0:
                response = None
                if limits:
                    if len(limits['parent_ids']) > 0:
                        response = get_people(
                            parent_event_ids=limits['parent_ids'],
                            labels=self.slugs,
                            roles=self.select_form.cleaned_data['roles'])
                else:
                    parent_items = []
                    for item in self.event_choices:
                        parent_items += [item[0]]
                    response = get_people(
                        parent_event_ids=parent_items,
                        labels=self.slugs,
                        roles=self.select_form.cleaned_data['roles'])
                if response:
                    people += response.people
            if "Class Coordinator" in self.priv_list:
                if limits is None or "Conference" in limits['labels']:
                    response = get_people(
                        label_sets=[self.slugs, ["Conference", ]],
                        roles=self.select_form.cleaned_data['roles'])
                    people += response.people
            if "Staff Lead" in self.priv_list:
                if limits:
                    if len(limits['labels']) > 0:
                        response = get_people(
                            label_sets=[self.slugs, limits['labels']],
                            roles=self.select_form.cleaned_data['roles'])
                else:
                    allowed_labels = ["Volunteer", ]
                    for area in self.staff_queryset:
                        allowed_labels += [area.slug]
                    response = get_people(
                        label_sets=[self.slugs, allowed_labels],
                        roles=self.select_form.cleaned_data['roles'])
                people += response.people
        for person in people:
            for user in person.users:
                person_contact = (user.email, user.profile.display_name)
                if user.profile.email_allowed(self.email_type) and (
                        person_contact not in to_list):
                    to_list += [person_contact]
            if person.public_class == "Bio":
                bio = Bio.objects.get(pk=person.public_id)
                person_contact = (bio.contact.user_object.email,
                                  bio.contact.display_name)
                if bio.contact.email_allowed(self.email_type) and (
                        person_contact not in to_list):
                    to_list += [person_contact]
        return sorted(to_list, key=lambda s: s[1].lower())

    def prep_email_form(self, request):
        to_list = self.get_to_list()
        recipient_info = SecretRoleInfoForm(request.POST,
                                            prefix="email-select")
        event_info = SelectEventForm(request.POST,
                                     prefix="event-select")
        event_info.fields['events'] = MultipleChoiceField(
            choices=self.event_choices,
            widget=MultipleHiddenInput(),
            required=False)
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
        event_info.fields['events'] = MultipleChoiceField(
            choices=self.event_choices,
            widget=MultipleHiddenInput(),
            required=False)
        context = self.get_select_forms()
        context["email_form"] = email_form
        context["recipient_info"] = [recipient_info, event_info]
        context["group_filter_note"] = self.filter_note()
        return render(
            request,
            self.template,
            context)

    def filter_preferences(self, basic_filter):
        return basic_filter.filter(
            Q(profile__preferences__isnull=True) |
            Q(profile__preferences__send_role_notifications=True))
