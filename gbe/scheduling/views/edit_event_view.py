from gbe.scheduling.views import ManageVolWizardView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from gbe.models import (
    Conference,
    Event,
)
from gbe.views.class_display_functions import get_scheduling_info
from gbe.scheduling.forms import PersonAllocationForm
from gbe.functions import validate_perms
from gbe_forms_text import (
    role_map,
    event_settings,
)
from scheduler.idd import get_occurrence
from gbe.scheduling.views.functions import (
    process_post_response,
    setup_event_management_form,
    show_scheduling_occurrence_status,
    shared_groundwork,
    update_event,
)


class EditEventView(ManageVolWizardView):
    template = 'gbe/scheduling/edit_event.tmpl'
    permissions = ('Scheduling Mavens',)
    title = "Edit Event"

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
            self.parent_id = self.occurrence.pk

        if self.item.type == "Show" and "/edit/" in request.path:
            return HttpResponseRedirect("%s?%s" % (
                reverse('edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              self.occurrence.pk]),
                request.GET.urlencode()))
        elif self.item.type == "Volunteer":
            return HttpResponseRedirect("%s?%s" % (
                reverse('edit_volunteer',
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
        return validity

    def make_context(self, request, errorcontext=None):
        context = super(EditEventView,
                        self).make_context(request, errorcontext)
        context, initial_form_info = setup_event_management_form(
            self.item.e_conference,
            self.item,
            self.occurrence,
            context)
        context['edit_title'] = self.title
        context['scheduling_info'] = get_scheduling_info(self.item)

        if 'worker_formset' not in context:
            context['worker_formset'] = self.make_formset(
                event_settings[self.item.type.lower()]['roles'])

        if validate_perms(request,
                          ('Volunteer Coordinator',), require=False):
            volunteer_initial_info = initial_form_info.copy()
            volunteer_initial_info.pop('occurrence_id')
            context.update(self.get_manage_opportunity_forms(
                volunteer_initial_info,
                self.manage_vol_url,
                self.conference,
                request,
                ['event', self.item.eventitem_id],
                errorcontext=errorcontext,
                occurrence_id=self.occurrence.pk))
        else:
            context['start_open'] = True

        return context

    def is_manage_opps(self, path):
        return "manage-opps" in path

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
        if self.is_manage_opps(request.path):
            return super(EditEventView, self).post(request, *args, **kwargs)
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        worker_formset = self.make_formset(
            event_settings[self.item.type.lower()]['roles'],
            post=request.POST)
        context, self.success_url, response = process_post_response(
            request,
            self.conference.conference_slug,
            self.item,
            self.success_url,
            "volunteer_open",
            self.occurrence.pk,
            self.is_formset_valid(worker_formset),
            worker_formset)
        context['worker_formset'] = worker_formset
        return self.make_post_response(request,
                                       response=response,
                                       errorcontext=context)
