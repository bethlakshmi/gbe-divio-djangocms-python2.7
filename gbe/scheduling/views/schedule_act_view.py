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
from django.urls import reverse
from gbe.models import (
    Act,
    Conference,
    Show,
)
from gbe.scheduling.forms import ActScheduleForm
from gbe.functions import validate_perms
from scheduler.data_transfer import (
    Commitment,
    Person,
)
from scheduler.idd import (
    get_people,
    get_occurrences,
    get_schedule,
    remove_booking,
    set_person,
)
from gbe.scheduling.views.functions import show_general_status


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
        if 'show_id' in list(request.GET.keys()):
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
            # TODO - this thread needs a regressive test
            messages.error(request, "Show id %d not found" % show_id)
            return self.select_shows(request)
        act_response = get_people(foreign_event_ids=[show.eventitem_id],
                                  roles=["Performer"])
        show_general_status(request, act_response, "ActScheduleView")
        if act_response.people:
            self.castings = sorted(act_response.people,
                                   key=lambda person: person.commitment.order)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        finish = self.groundwork(request, args, kwargs)
        if finish:
            return finish
        forms = []
        if len(self.castings) == 0:
            messages.error(request, "No Acts have been cast in this show")
        for casting in self.castings:
            act = Act.objects.get(pk=casting.commitment.class_id)
            details = {}
            details['title'] = act.b_title
            details['performer'] = act.performer
            details['show'] = self.show_event.pk
            details['booking_id'] = casting.booking_id
            details['order'] = casting.commitment.order
            forms += [(ActScheduleForm(initial=details,
                                       show_choices=self.show_choices,
                                       prefix=act.pk),
                       act.performer.contact.user_object.is_active)]
        return render(request,
                      self.template,
                      {'title': "Schedule Acts for %s" % str(self.show_event),
                       'forms': forms})

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        finish = self.groundwork(request, args, kwargs)
        if finish:
            return finish
        forms = []
        error_forms = []
        success_msg = ""
        for casting in self.castings:
            act = Act.objects.get(pk=casting.commitment.class_id)
            form = ActScheduleForm(request.POST,
                                   show_choices=self.show_choices,
                                   prefix=act.pk)
            if form.is_valid():
                forms += [(form, act)]
            else:
                error_forms += [(
                    form,
                    act.performer.contact.user_object.is_active)]

        if len(error_forms) > 0:
            for form, act in forms:
                error_forms += [(form,
                                 act.performer.contact.user_object.is_active)]
            return render(
                request,
                self.template, {
                    'forms': error_forms,
                    'title': "Schedule Acts for %s" % str(self.show_event)})
        else:
            for form, act in forms:
                person = Person(public_id=act.performer.pk,
                                booking_id=form.cleaned_data['booking_id'],
                                role="Performer",
                                commitment=Commitment(
                                    decorator_class=act,
                                    order=form.cleaned_data['order']))
                if int(form.cleaned_data['show']) != self.show_event.pk:
                    sched_response = get_schedule(commitment=act)
                    for item in sched_response.schedule_items:
                        if item.booking_id != int(
                                form.cleaned_data['booking_id']):
                            remove_response = remove_booking(
                                item.event.pk,
                                item.booking_id)
                            if remove_response.booking_id == item.booking_id:
                                messages.success(
                                    request,
                                    "Removed Rehearsal Booking: rehearsal - " +
                                    "%s, performer - %s" % (
                                        str(item.event),
                                        str(act.performer)))
                            else:
                                messages.error(
                                    request,
                                    "Could not clear rehearsal: %s" % str(
                                        item.event))
                response = set_person(person=person,
                                      occurrence_id=form.cleaned_data['show'])

                # we don't care about overbook warnings on this case
                response.warnings = []
                show_general_status(request, response, "ActScheduleView")
                if response.occurrence:
                    success_msg = self.entry % (
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
