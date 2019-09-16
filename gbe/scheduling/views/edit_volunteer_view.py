from gbe.scheduling.views import ManageWorkerView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from gbe.functions import validate_perms
from gbe.scheduling.views.functions import (
    process_post_response,
    setup_event_management_form,
    show_scheduling_occurrence_status,
    shared_groundwork,
    update_event,
)


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
            (self.profile, self.occurrence, self.item) = groundwork_data
            self.conference = self.item.e_conference
        if self.item.type != "Volunteer":
            return HttpResponseRedirect("%s?%s" % (
                reverse('edit_event',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              self.occurrence.pk]),
                request.GET.urlencode()))
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
            self.item.e_conference,
            self.item,
            self.occurrence,
            context)
        context['edit_title'] = self.title

        if validate_perms(request,
                          ('Volunteer Coordinator',),
                          require=False):
            context.update(self.get_worker_allocation_forms(
                errorcontext=errorcontext))
            context.update(self.get_volunteer_info())
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
        if response and hasattr(response, 'occurrence'):
            show_scheduling_occurrence_status(
                request,
                response,
                self.__class__.__name__)
            return HttpResponseRedirect(self.success_url)
        return super(EditVolunteerView,
                     self).make_post_response(request, response, errorcontext)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        return render(request, self.template, self.make_context(request))

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        if "manage-workers" in request.path:
            return super(EditVolunteerView,
                         self).post(request, *args, **kwargs)
        context, self.success_url, response = process_post_response(
            request,
            self.conference.conference_slug,
            self.item,
            self.success_url,
            "worker_open",
            self.occurrence.pk)
        return self.make_post_response(request,
                                       response=response,
                                       errorcontext=context)
