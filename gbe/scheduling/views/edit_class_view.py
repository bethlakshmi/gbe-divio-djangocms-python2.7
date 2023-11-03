from gbe.scheduling.views import EditEventView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from datetime import timedelta
from gbe.models import (
    Class,
    Conference,
)
from gbe.views.class_display_functions import get_scheduling_info
from gbe.scheduling.forms import (
    ClassBookingForm,
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


class EditClassView(EditEventView):
    title = "Edit Class"
    event_form_class = ClassBookingForm

    def groundwork(self, request, args, kwargs):
        error_url = super(EditClassView,
                          self).groundwork(request, args, kwargs)
        if error_url:
            return error_url
        self.success_url = reverse('edit_class',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.conference.conference_slug,
                                         self.occurrence.pk])

    def make_context(self, request, errorcontext=None):
        context = super(EditClassView,
                        self).make_context(request, errorcontext)
        class_bid = Class.objects.get(pk=self.occurrence.connected_id)
        if context['event_form'].__class__ != self.event_form_class:
            context['event_form'] = self.event_form_class(
                instance=class_bid,
                initial={'slug': self.occurrence.slug})
        context['scheduling_info'] = get_scheduling_info(class_bid)
        return context

    def setup_event_post_form(self, request):
        return self.event_form_class(
            request.POST,
            instance=Class.objects.get(pk=self.occurrence.connected_id))

    def update_event(self, context, people):
        m = context['scheduling_form'].cleaned_data['duration']*60
        max_v = context['scheduling_form'].cleaned_data['max_volunteer']
        r = event_settings[self.occurrence.event_style.lower()]['roles']
        l = [context['scheduling_form'].cleaned_data['location']]
        response = update_occurrence(
            self.occurrence.pk,
            context['event_form'].cleaned_data['b_title'],
            context['event_form'].cleaned_data['b_description'],
            get_start_time(context['scheduling_form'].cleaned_data),
            length=timedelta(minutes=m),
            max_volunteer=max_v,
            people=people,
            roles=r,
            locations=l,
            approval=context['scheduling_form'].cleaned_data['approval'],
            slug=context['event_form'].cleaned_data['slug'])
        if response.occurrence:
            class_bid = context['event_form'].save()
        return response
