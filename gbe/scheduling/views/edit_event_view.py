from gbe.scheduling.views import ManageVolWizardView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import timedelta
from gbe.models import Conference
from gbe.scheduling.forms import (
    EventBookingForm,
    PersonAllocationForm,
    ScheduleOccurrenceForm,
)
from gbe.functions import validate_perms
from gbe_forms_text import (
    role_map,
    event_settings,
)
from gbe.scheduling.views.functions import (
    get_start_time,
    setup_event_management_form,
    show_scheduling_occurrence_status,
    shared_groundwork,
)
from scheduler.idd import update_occurrence
from scheduler.data_transfer import Person


class EditEventView(ManageVolWizardView):
    template = 'gbe/scheduling/edit_event.tmpl'
    permissions = ('Scheduling Mavens',)
    title = "Edit Event"
    event_form_class = EventBookingForm

    def groundwork(self, request, args, kwargs):
        groundwork_data = shared_groundwork(request, kwargs, self.permissions)
        if groundwork_data is None:
            error_url = reverse('manage_event_list',
                                urlconf='gbe.scheduling.urls',
                                args=[kwargs['conference']])
            return HttpResponseRedirect(error_url)
        else:
            (self.profile, self.occurrence) = groundwork_data
            self.conference = Conference.objects.get(
                conference_slug__in=self.occurrence.labels)
            self.parent_id = self.occurrence.pk

        # TO DO - rework the request.GET.urlencode - it's a bad security
        # practice.  But there's a enough complexity here, I want it as a
        # separate change
        if self.occurrence.event_style == "Show" and "/edit/" in request.path:
            return HttpResponseRedirect("%s?%s" % (
                reverse('edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              self.occurrence.pk]),
                request.GET.urlencode()))
        elif self.occurrence.event_style == "Volunteer":
            return HttpResponseRedirect("%s?%s" % (
                reverse('edit_volunteer',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              self.occurrence.pk]),
                request.GET.urlencode()))
        elif self.occurrence.connected_class == "Class" and (
                "/edit/" in request.path):
            return HttpResponseRedirect("%s?%s" % (
                reverse('edit_class',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              self.occurrence.pk]),
                request.GET.urlencode()))
        self.manage_vol_url = reverse('manage_vol',
                                      urlconf='gbe.scheduling.urls',
                                      args=[self.conference.conference_slug,
                                            self.occurrence.pk])
        self.success_url = reverse('edit_event',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.conference.conference_slug,
                                         self.occurrence.pk])

    def make_formset(self, roles, post=None):
        formset = []
        n = 0
        for booking in self.occurrence.people:
            if booking.role in role_map:
                formset += [PersonAllocationForm(
                    post,
                    label_visible=False,
                    role_options=[(booking.role, booking.role), ],
                    use_personas=role_map[booking.role],
                    initial={
                        'role': booking.role,
                        'worker': booking.public_id,
                    },
                    prefix="alloc_%d" % n)]
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
        if len(formset) == 0:
            validity = True
        return validity

    def make_context(self, request, errorcontext=None):
        context = super(EditEventView,
                        self).make_context(request, errorcontext)
        context, initial_form_info = setup_event_management_form(
            self.conference,
            self.occurrence,
            context)
        context['edit_title'] = self.title

        if 'worker_formset' not in context:
            context['worker_formset'] = self.make_formset(
                event_settings[self.occurrence.event_style.lower()]['roles'])

        if validate_perms(request,
                          ('Volunteer Coordinator',), require=False):
            volunteer_initial_info = initial_form_info.copy()
            volunteer_initial_info.pop('occurrence_id')
            context.update(self.get_manage_opportunity_forms(
                volunteer_initial_info,
                self.manage_vol_url,
                self.conference,
                request,
                errorcontext=errorcontext,
                occurrence_id=self.occurrence.pk))
        else:
            context['start_open'] = True

        return context

    def is_manage_opps(self, path):
        return "manage-opps" in path

    @method_decorator(never_cache, name="get")
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        return render(request, self.template, self.make_context(request))

    @method_decorator(never_cache, name="post")
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if self.is_manage_opps(request.path):
            return super(EditEventView, self).post(request, *args, **kwargs)
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        worker_formset = self.make_formset(
            event_settings[self.occurrence.event_style.lower()]['roles'],
            post=request.POST)

        response = None
        context = {
            'event_form': self.setup_event_post_form(request),
            'scheduling_form': ScheduleOccurrenceForm(
                request.POST,
                conference=self.conference,
                open_to_public=event_settings[
                    self.occurrence.event_style.lower()]['open_to_public'])
        }
        if context['event_form'].is_valid(
                ) and context['scheduling_form'].is_valid(
                ) and self.is_formset_valid(worker_formset):
            people = []
            for assignment in worker_formset:
                if assignment.is_valid() and assignment.cleaned_data['worker']:
                    worker = assignment.cleaned_data['worker']
                    if worker.__class__.__name__ == "Bio":
                        user_object = worker.contact.user_object
                    else:
                        user_object = worker.user_object
                    people += [Person(
                        users=[user_object],
                        public_id=worker.pk,
                        public_class=worker.__class__.__name__,
                        role=assignment.cleaned_data['role'])]
            if len(people) == 0:
                people = None

            response = self.update_event(context, people)

            if request.POST.get('edit_event', 0) != "Save and Continue":
                self.success_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
                    reverse('manage_event_list',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]),
                    self.conference.conference_slug,
                    context['scheduling_form'].cleaned_data['day'].pk,
                    str([self.occurrence.pk]),)
            else:
                self.success_url = "%s?%s=True" % (self.success_url,
                                                   "volunteer_open")
        else:
            context['start_open'] = True

        context['worker_formset'] = worker_formset
        return self.make_post_response(request,
                                       response=response,
                                       errorcontext=context)

    def setup_event_post_form(self, request):
        return self.event_form_class(request.POST)

    def update_event(self, context, people):
        m = context['scheduling_form'].cleaned_data['duration']*60
        max_v = context['scheduling_form'].cleaned_data['max_volunteer']
        r = event_settings[self.occurrence.event_style.lower()]['roles']
        l = [context['scheduling_form'].cleaned_data['location']]
        response = update_occurrence(
            self.occurrence.pk,
            context['event_form'].cleaned_data['title'],
            context['event_form'].cleaned_data['description'],
            get_start_time(context['scheduling_form'].cleaned_data),
            length=timedelta(minutes=m),
            max_volunteer=max_v,
            people=people,
            roles=r,
            locations=l,
            approval=context['scheduling_form'].cleaned_data['approval'],
            slug=context['event_form'].cleaned_data['slug'])
        return response
