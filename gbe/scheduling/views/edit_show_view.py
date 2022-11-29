from gbe.scheduling.views import EditEventView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from gbe.scheduling.forms import RehearsalSlotForm
from gbe.scheduling.views.functions import show_general_status
from gbe.functions import get_conference_day
from gbetext import rehearsal_delete_msg
from scheduler.idd import (
    get_bookings,
    get_occurrences,
    create_occurrence,
    delete_occurrence,
    update_occurrence,
)
from datetime import timedelta
from django.contrib import messages
from gbe.models import UserMessage


class EditShowView(EditEventView):
    template = 'gbe/scheduling/edit_event.tmpl'
    permissions = ('Scheduling Mavens',)
    title = "Edit Show"
    window_controls = ['start_open', 'volunteer_open', 'rehearsal_open']

    def groundwork(self, request, args, kwargs):
        error_url = super(EditShowView,
                          self).groundwork(request, args, kwargs)
        if error_url:
            return error_url
        self.manage_vol_url = reverse('manage_show_opp',
                                      urlconf='gbe.scheduling.urls',
                                      args=[kwargs['conference'],
                                            kwargs['occurrence_id']])
        self.success_url = reverse('edit_show',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.conference.conference_slug,
                                         self.occurrence.pk])

    def get_rehearsal_forms(self,
                            initial,
                            manage_slot_info,
                            conference,
                            request,
                            errorcontext,
                            occurrence_id):
        '''
        Generate the forms to allocate, edit, or delete volunteer
        opportunities associated with a scheduler event.
        '''
        actionform = []
        context = {}
        response = get_occurrences(parent_event_id=occurrence_id)

        for rehearsal_slot in response.occurrences:
            rehearsal = None
            if rehearsal_slot.event_style == "Rehearsal Slot":
                if (errorcontext and 'error_slot_form' in errorcontext and
                        errorcontext['error_slot_occurrence_id'
                                     ] == int(rehearsal_slot.pk)):
                    actionform.append(errorcontext['error_slot_form'])
                else:
                    max_commitments = rehearsal_slot.max_commitments
                    date = rehearsal_slot.start_time.date()

                    time = rehearsal_slot.start_time.time
                    day = get_conference_day(
                        conference=conference,
                        date=date)
                    location = rehearsal_slot.location
                    if location:
                        room = location.room
                    elif self.occurrence.location:
                        room = self.occurrence.location.room
                    response = get_bookings(
                        [rehearsal_slot.pk],
                        roles=["Performer"])
                    actionform.append(
                        RehearsalSlotForm(
                            conference=conference,
                            initial={'opp_sched_id': rehearsal_slot.pk,
                                     'title': rehearsal_slot.title,
                                     'duration': rehearsal_slot.duration,
                                     'event_style': rehearsal_slot.event_style,
                                     'current_acts': len(response.people),
                                     'max_volunteer': max_commitments,
                                     'day': day,
                                     'time': time,
                                     'location': room,
                                     },
                            )
                        )
        context['slotactionform'] = actionform
        if errorcontext and 'createslotform' in errorcontext:
            createform = errorcontext['createslotform']
        else:
            createform = RehearsalSlotForm(
                prefix='new_slot',
                initial=initial,
                conference=conference)

        actionheaders = ['Title',
                         'Booked/',
                         'Available',
                         'Duration',
                         'Day',
                         'Time',
                         'Location']
        context.update({'createslotform': createform,
                        'slotactionheaders': actionheaders,
                        'manage_slot_url': manage_slot_info}),
        return context

    def make_context(self, request, errorcontext=None):
        context = super(EditShowView,
                        self).make_context(request, errorcontext=errorcontext)
        initial_rehearsal_info = {
                'type':  "Rehearsal Slot",
                'duration': 1.0,
                'max_volunteer': 10,
                'day': get_conference_day(
                    conference=self.conference,
                    date=self.occurrence.starttime.date()),
                'time': (self.occurrence.starttime - timedelta(hours=4)
                         ).strftime("%H:%M:%S"),
                'location': self.occurrence.location,
                'occurrence_id': self.occurrence.pk, }
        context.update(self.get_rehearsal_forms(
                initial_rehearsal_info,
                self.manage_vol_url,
                self.conference,
                request,
                errorcontext=errorcontext,
                occurrence_id=self.occurrence.pk))
        return context

    def is_manage_opps(self, path):
        return "manage-opps" in path or "manage-show-opps" in path

    def do_additional_actions(self, request):
        response = None
        context = None
        if ('create_slot' in list(request.POST.keys())) or (
                'duplicate_slot' in list(request.POST.keys())):
            self.create = True
            if 'create_slot' in list(request.POST.keys()):
                self.event_form = RehearsalSlotForm(
                    request.POST,
                    prefix='new_slot',
                    conference=self.conference)
            else:
                self.event_form = RehearsalSlotForm(
                    request.POST,
                    conference=self.conference)
            if self.event_form.is_valid():
                data = self.get_basic_form_settings()
                response = create_occurrence(
                    data['title'],
                    data['duration'],
                    data['event_style'],
                    self.start_time,
                    max_commitments=self.max_volunteer,
                    locations=[self.room],
                    labels=data['labels'],
                    parent_event_id=self.parent_id)
            else:
                context = {'createslotform': self.event_form,
                           'rehearsal_open': True}
        elif 'edit_slot' in list(request.POST.keys()):
            casting_response = get_bookings(
                        [int(request.POST['opp_sched_id'])],
                        roles=["Performer"])
            self.event_form = RehearsalSlotForm(
                request.POST,
                conference=self.conference,
                initial={'current_acts': len(casting_response.people)})
            if self.event_form.is_valid():
                data = self.get_basic_form_settings()
                response = update_occurrence(
                    data['opp_sched_id'],
                    title=data['title'],
                    start_time=self.start_time,
                    length=data['duration'],
                    max_commitments=self.max_volunteer,
                    locations=[self.room])
            else:
                context = {
                    'error_slot_form': self.event_form,
                    'error_slot_occurrence_id': int(
                        request.POST['opp_sched_id']),
                    'rehearsal_open': True}
        elif 'delete_slot' in list(request.POST.keys()):
            response = delete_occurrence(request.POST['opp_sched_id'])
            show_general_status(request, response, self.__class__.__name__)
            if not response.errors:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="DELETE_REHEARSAL_SUCCESS",
                    defaults={
                        'summary': "Rehearsal Slot Deleted",
                        'description': rehearsal_delete_msg})
                messages.success(
                    request,
                    '%s' % user_message[0].description)
                return HttpResponseRedirect(self.success_url)
        return self.check_success_and_return(
            request,
            response=response,
            errorcontext=context,
            window_controls="rehearsal_open=True")
