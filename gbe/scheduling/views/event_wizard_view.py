from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.functions import validate_perms
from django.urls import reverse
from scheduler.data_transfer import Person
from scheduler.idd import create_occurrence
from gbe.scheduling.forms import (
    PersonAllocationForm,
    PickEventForm,
)
from gbe.models import Conference
from gbe.scheduling.views.functions import (
    get_start_time,
    show_scheduling_occurrence_status,
)
from gbe_forms_text import role_map
from gbetext import calendar_for_event
from datetime import timedelta


class EventWizardView(View):
    template = 'gbe/scheduling/event_wizard.tmpl'
    permissions = ('Scheduling Mavens',)
    default_event_type = None

    def get_pick_event_form(self, request):
        if 'pick_event' in list(request.GET.keys()):
            return PickEventForm(request.GET)
        elif self.default_event_type:
            return PickEventForm(initial={
                'event_type': self.default_event_type})
        else:
            return PickEventForm()

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        if "conference" in kwargs:
            self.conference = get_object_or_404(
                Conference,
                conference_slug=kwargs['conference'])
        context = {
            'selection_form':  self.get_pick_event_form(request),
            'conference_slug': self.conference.conference_slug,
        }
        return context

    @method_decorator(never_cache, name="get")
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        if 'pick_event' in list(request.GET.keys()) and context[
                'selection_form'].is_valid():
            if context['selection_form'].cleaned_data[
                    'event_type'] == 'conference':
                return HttpResponseRedirect("%s?%s" % (
                    reverse('create_class_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]),
                    request.GET.urlencode()))
            if context['selection_form'].cleaned_data[
                    'event_type'] == 'staff':
                return HttpResponseRedirect("%s?%s" % (
                    reverse('staff_area_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]),
                    request.GET.urlencode()))
            if context['selection_form'].cleaned_data[
                    'event_type'] == 'rehearsal':
                return HttpResponseRedirect("%s?%s" % (
                    reverse('rehearsal_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]),
                    request.GET.urlencode()))
            if context['selection_form'].cleaned_data[
                    'event_type'] == 'volunteer':
                return HttpResponseRedirect("%s?%s" % (
                    reverse('create_volunteer_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]),
                    request.GET.urlencode()))
            if context['selection_form'].cleaned_data[
                    'event_type'] in ('drop-in', 'master', 'show', 'special'):
                return HttpResponseRedirect("%s?%s" % (
                    reverse('create_ticketed_event_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug,
                                  context['selection_form'].cleaned_data[
                                    'event_type']]),
                    request.GET.urlencode()))
        return render(request, self.template, context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EventWizardView, self).dispatch(*args, **kwargs)

    def make_formset(self, roles, initial=None, post=None):
        formset = []
        n = 0
        if initial:
            formset += [PersonAllocationForm(
                post,
                label_visible=False,
                role_options=[(initial['role'], initial['role']), ],
                use_personas=role_map[initial['role']],
                initial=initial,
                prefix="alloc_0")]
            n = n + 1
        for role in roles:
            formset += [PersonAllocationForm(
                post,
                label_visible=False,
                role_options=[(role, role), ],
                use_personas=role_map[role],
                initial={'role': role},
                prefix="alloc_%d" % n), ]
            n = n + 1
        return formset

    def is_formset_valid(self, formset):
        validity = False
        for form in formset:
            validity = form.is_valid() or validity
        return validity

    def book_event(self,
                   event_form,
                   scheduling_form,
                   people_formset,
                   event_style):
        start_time = get_start_time(scheduling_form.cleaned_data)
        labels = [self.conference.conference_slug]
        if calendar_for_event[event_style]:
                labels += [calendar_for_event[event_style]]
        people = []
        for assignment in people_formset:
            if assignment.is_valid() and assignment.cleaned_data['worker']:
                worker = assignment.cleaned_data['worker']
                user_object = None
                if worker.__class__.__name__ == "Bio":
                    user_object = worker.contact.user_object
                else:
                    user_object = worker.user_object
                people += [Person(
                    users=[user_object],
                    public_id=worker.pk,
                    public_class=worker.__class__.__name__,
                    role=assignment.cleaned_data['role'])]
        response = create_occurrence(
            event_form.cleaned_data['title'],
            timedelta(minutes=scheduling_form.cleaned_data['duration']*60),
            event_style,
            start_time,
            scheduling_form.cleaned_data['max_volunteer'],
            people=people,
            locations=[scheduling_form.cleaned_data['location']],
            description=event_form.cleaned_data['description'],
            labels=labels,
            approval=scheduling_form.cleaned_data['approval'],
            slug=event_form.cleaned_data['slug'])
        return response

    def finish_booking(self, request, response, day_pk):
        show_scheduling_occurrence_status(
            request,
            response,
            self.__class__.__name__)
        if response.occurrence:
            return HttpResponseRedirect(
                "%s?%s-day=%d&filter=Filter&new=%s" % (
                    reverse('manage_event_list',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]),
                    self.conference.conference_slug,
                    day_pk,
                    str([response.occurrence.pk]),))
