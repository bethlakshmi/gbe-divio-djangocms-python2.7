from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from gbe.models import (
    Act,
    Conference,
    Show,
)
from gbe.scheduling.forms import ActScheduleForm
from gbe.functions import validate_perms
from scheduler.data_transfer import BookableAct
from scheduler.idd import (
    get_acts,
    get_occurrences,
    set_act,
)
from gbe.scheduling.views.functions import (
    process_post_response,
    setup_event_management_form,
    show_general_status,
    shared_groundwork,
    update_event,
)


class ScheduleAct(View):
    template = 'gbe/scheduling/act_schedule.tmpl'
    permissions = ('Scheduling Mavens',)
    entry = "%s<li>Performer: %s, Act: %s - Show: %s, Order: %d</li>"

    def select_shows(self, request):
        template = 'gbe/scheduling/select_show.tmpl'
        show_options = Show.objects.exclude(e_conference__status='completed')
        return render(request, template, {'show_options': show_options})

    def groundwork(self, request, args, kwargs):
        self.show_event = None
        self.castings = []
        validate_perms(request, self.permissions)
        if 'show_id' in request.GET.keys():
            show_id = int(request.GET['show_id'])
        elif 'show_id' in kwargs:
            show_id = kwargs['show_id']
        else:
            return self.select_shows(request)

        show = get_object_or_404(Show, pk=show_id)
        show_ids = Show.objects.filter(
            e_conference=show.e_conference).values('eventitem_id')
        response = get_occurrences(foreign_event_ids=show_ids)
        show_general_status(request, response, "ActScheduleView")
        self.show_choices = []
        for occurrence in response.occurrences:
            self.show_choices += [(occurrence.pk, str(occurrence))]
            if occurrence.eventitem.eventitem_id == show.eventitem_id:
                self.show_event = occurrence
        if not self.show_event:
            messages.error(request, "Show id %d not found" % show_id)
            return self.select_shows(request)
        act_response = get_acts(self.show_event.pk)
        show_general_status(request, act_response, "ActScheduleView")
        if act_response.castings:
            self.castings = act_response.castings

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        finish =  self.groundwork(request, args, kwargs)
        if finish:
            return finish
        forms = []
        if len(self.castings) == 0:
            messages.error("No Acts have been cast in this show")
        for casting in self.castings:
            act = Act.objects.get(resourceitem_id=casting.act)
            details = {}
            details['title'] = act.b_title
            details['performer'] = act.performer
            details['show'] = self.show_event.pk
            details['booking_id'] = casting.booking_id
            if casting.order:
                details['order'] = casting.order
            else:
                details['order'] = 0
            forms += [(ActScheduleForm(initial=details,
                                       show_choices=self.show_choices,
                                       prefix=casting.act),
                       act.performer.contact.user_object.is_active)]
        return render(request,
                      self.template,
                      {'title': "Schedule Acts for %s" % str(self.show_event),
                       'forms': forms})

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        finish =  self.groundwork(request, args, kwargs)
        if finish:
            return finish
        forms = []
        error_forms = []
        success_msg = ""
        for casting in self.castings:
            act = Act.objects.get(resourceitem_id=casting.act)
            form = ActScheduleForm(request.POST,
                                   show_choices=self.show_choices,
                                   prefix=casting.act)
            if form.is_valid():
                forms += [(form, act)]
            else:
                error_forms += [(form, 
                                 act.performer.contact.user_object.is_active)]

        if len(error_forms) > 0:
            for form, act in forms:
                error_forms += [(form,
                                 act.performer.contact.user_object.is_active)]
            return render(request,
                   self.template,
                   {'forms': error_forms,
                    'title': "Schedule Acts for %s" % str(self.show_event)})
        else:
            for form, act in forms:
                bookable_act = BookableAct(
                    act=act,
                    booking_id=form.cleaned_data['booking_id'],
                    order=form.cleaned_data['order'])
                response = set_act(occurrence_id=form.cleaned_data['show'],
                                   act=bookable_act)
                # we don't care about overbook warnings on this case
                response.warnings = []
                show_general_status(request, response, "ActScheduleView")
                if response.occurrence:
                    success_msg =  self.entry % (
                        success_msg,
                        str(act.performer),
                        act.b_title,
                        str(response.occurrence),
                        form.cleaned_data['order'])
        if len(success_msg) > 0:
            messages.success(request, success_msg)
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    def dispatch(self, *args, **kwargs):
        return super(ScheduleAct, self).dispatch(*args, **kwargs)
