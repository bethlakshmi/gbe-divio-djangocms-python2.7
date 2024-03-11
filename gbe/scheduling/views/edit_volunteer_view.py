from gbe.scheduling.views import ManageWorkerView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from gbe.functions import validate_perms
from gbe.scheduling.views.functions import (
    get_start_time,
    setup_event_management_form,
    show_scheduling_occurrence_status,
    shared_groundwork,
)
from gbe.scheduling.forms import (
    EventAssociationForm,
    EventBookingForm,
    ScheduleOccurrenceForm,
)
from django.forms.widgets import CheckboxInput
from gbe.models import (
    Conference,
    StaffArea,
)
from gbe_forms_text import event_settings
from gbetext import calendar_for_event
from datetime import timedelta
from scheduler.idd import update_occurrence


class EditVolunteerView(ManageWorkerView):
    template = 'gbe/scheduling/edit_event.tmpl'
    permissions = ('Scheduling Mavens',)
    title = "Edit Volunteer Opportunity"

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
        if self.occurrence.event_style != "Volunteer":
            return HttpResponseRedirect("%s?%s" % (
                reverse('edit_event',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              self.occurrence.pk]),
                request.GET.urlencode()))
        self.area = StaffArea.objects.filter(
                conference=self.conference,
                slug__in=self.occurrence.labels).first()
        self.parent_id = -1
        if self.occurrence.parent is not None:
            self.parent_id = self.occurrence.parent.pk
        self.peer_id = -1
        if self.occurrence.peer is not None:
            self.peer_id = self.occurrence.peer.pk
        self.manage_worker_url = reverse('manage_workers',
                                         urlconf='gbe.scheduling.urls',
                                         args=[self.conference.conference_slug,
                                               self.occurrence.pk])
        self.success_url = reverse('edit_volunteer',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.conference.conference_slug,
                                         self.occurrence.pk])

    def make_context(self, request, errorcontext=None):
        context = super(EditVolunteerView,
                        self).make_context(request, errorcontext)
        context, initial_form_info = setup_event_management_form(
            self.conference,
            self.occurrence,
            context,
            open_to_public=False)

        if 'association_form' not in context:
            context['association_form'] = EventAssociationForm(initial={
              'staff_area': self.area,
              'parent_event': self.parent_id,
              'peer_event': self.peer_id,
              'conference': self.conference})
        context['edit_title'] = self.title
        context['scheduling_form'].fields['approval'].widget = CheckboxInput()

        if validate_perms(request,
                          ('Volunteer Coordinator',),
                          require=False):
            context.update(self.get_worker_allocation_forms(
                errorcontext=errorcontext))
            if self.request.GET.get('changed_id', None):
                context['changed_id'] = int(
                    self.request.GET.get('changed_id', None))
        else:
            context['start_open'] = True

        return context

    def make_post_response(self,
                           request,
                           response=None,
                           errorcontext=None):
        if response and hasattr(response, 'occurrence') and not hasattr(
                response, 'booking_id'):
            show_scheduling_occurrence_status(
                request,
                response,
                self.__class__.__name__)
            return HttpResponseRedirect(self.success_url)
        return super(EditVolunteerView,
                     self).make_post_response(request, response, errorcontext)

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
        context = {}
        response = None
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        if "manage-workers" in request.path:
            return super(EditVolunteerView,
                         self).post(request, *args, **kwargs)
        context['association_form'] = EventAssociationForm(
            request.POST,
            initial={'staff_area': self.area,
                     'parent_event': self.parent_id,
                     'peer_event': self.peer_id,
                     'conference': self.conference})
        context['event_form'] = EventBookingForm(request.POST)
        context['scheduling_form'] = ScheduleOccurrenceForm(
            request.POST,
            conference=self.conference,
            open_to_public=event_settings[self.occurrence.event_style.lower()][
                'open_to_public'])

        if context['event_form'].is_valid(
                ) and context['scheduling_form'].is_valid(
                ) and context['association_form'].is_valid():
            duration = timedelta(
                minutes=context['scheduling_form'].cleaned_data['duration']*60)
            labels = [calendar_for_event[self.occurrence.event_style],
                      self.conference.conference_slug]
            if context['association_form'].cleaned_data['staff_area']:
                labels += [
                    context['association_form'].cleaned_data['staff_area'].slug
                    ]
            parent_id = -1
            if context['association_form'].cleaned_data['parent_event']:
                parent_id = int(
                    context['association_form'].cleaned_data['parent_event'])
            peer_id = -1
            if context['association_form'].cleaned_data['peer_event']:
                peer_id = context['association_form'].cleaned_data[
                    'peer_event'].pk
            response = update_occurrence(
                self.occurrence.pk,
                title=context['event_form'].cleaned_data['title'],
                description=context['event_form'].cleaned_data['description'],
                length=duration,
                start_time=get_start_time(
                    context['scheduling_form'].cleaned_data),
                max_volunteer=context[
                    'scheduling_form'].cleaned_data['max_volunteer'],
                people=None,
                roles=None,
                locations=[
                    context['scheduling_form'].cleaned_data['location']],
                approval=context['scheduling_form'].cleaned_data['approval'],
                labels=labels,
                parent_event_id=parent_id,
                peer_id=peer_id,
                slug=context['event_form'].cleaned_data['slug'])

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
                                                   "worker_open")
        else:
            context['start_open'] = True

        return self.make_post_response(request,
                                       response=response,
                                       errorcontext=context)
