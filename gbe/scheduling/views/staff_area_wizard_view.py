from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from gbe.models import UserMessage
from gbe.scheduling.forms import (
    StaffAreaForm,
)
from gbe.scheduling.views import EventWizardView
from gbe.duration import Duration
from gbe.functions import validate_perms
from gbe_forms_text import event_settings


class StaffAreaWizardView(EventWizardView):
    template = 'gbe/scheduling/ticketed_event_wizard.tmpl'
    event_type = "staff"

    def groundwork(self, request, args, kwargs):
        context = super(StaffAreaWizardView,
                        self).groundwork(request, args, kwargs)
        context['event_type'] = "Staff Area"
        context['second_title'] = "Create Staff Area"
        context['volunteer_scheduling'] = validate_perms(
            request,
            ('Volunteer Coordinator',),
            require=False)
        return context

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = StaffAreaForm(
            initial={'conference':  self.conference})
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = StaffAreaForm(
            request.POST,
            initial={'conference':  self.conference})
        if context['second_form'].is_valid():
            new_event = context['second_form'].save()
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="STAFF_AREA_CREATE_SUCCESS",
                defaults={
                    'summary': "Staff area has been created",
                    'description': "Staff area has been created."})
            messages.success(
                request,
                '%s<br>Title: %s' % (
                    user_message[0].description,
                    new_event.title))
            if request.POST.get(
                    'set_event'
                    ) == 'More...' and (
                    context['volunteer_scheduling']):
                return HttpResponseRedirect(
                    "%s?start_open=False" %
                    reverse('edit_staff',
                            urlconf='gbe.scheduling.urls',
                            args=[new_event.id]))
            else:
                return HttpResponseRedirect(
                    reverse('manage_event_list',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug]))
        return render(request, self.template, context)
