from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from gbe.scheduling.forms import PickShowForm
from gbe.scheduling.views import EventWizardView


class RehearsalWizardView(EventWizardView):
    template = 'gbe/scheduling/rehearsal_wizard.tmpl'
    roles = ['Staff Lead', ]
    default_event_type = "rehearsal"

    def groundwork(self, request, args, kwargs):
        context = super(RehearsalWizardView,
                        self).groundwork(request, args, kwargs)
        context['event_type'] = "Rehearsal Slot"
        context['second_title'] = "Choose the Show for This Slot"
        return context

    @method_decorator(never_cache, name="get")
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickShowForm(
            initial={'conference':  self.conference})
        return render(request, self.template, context)

    @method_decorator(never_cache, name="post")
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        working_class = None
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickShowForm(
            request.POST,
            initial={'conference':  self.conference})
        context['third_title'] = "Make New Rehearsal Slot"
        if 'pick_show' in list(request.POST.keys()) and context[
                'second_form'].is_valid():
            if context['second_form'].cleaned_data['show']:
                show_id = context['second_form'].cleaned_data['show']
                return HttpResponseRedirect(
                    "%s?rehearsal_open=True" % reverse(
                        'edit_show',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              show_id]))
            else:
                return HttpResponseRedirect("%s?%s" % (
                    reverse('create_ticketed_event_wizard',
                            urlconf='gbe.scheduling.urls',
                            args=[self.conference.conference_slug,
                                  "show"]),
                    request.GET.urlencode()))
        return render(request, self.template, context)
