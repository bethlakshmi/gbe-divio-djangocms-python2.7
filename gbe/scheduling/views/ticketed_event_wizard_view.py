from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from gbe.models import UserMessage
from gbe.scheduling.forms import (
    GenericBookingForm,
    ScheduleOccurrenceForm,
    ShowBookingForm,
)
from gbe.scheduling.views import EventWizardView
from ticketing.forms import LinkTicketsForm
from gbe.functions import validate_perms
from gbetext import link_event_to_ticket_success_msg
from gbe_forms_text import event_settings


class TicketedEventWizardView(EventWizardView):
    template = 'gbe/scheduling/ticketed_event_wizard.tmpl'
    roles = ['Producer',
             'Technical Director',
             'Teacher',
             'Volunteer',
             'Staff Lead']
    default_event_type = "general"

    def groundwork(self, request, args, kwargs):
        context = super(TicketedEventWizardView,
                        self).groundwork(request, args, kwargs)
        self.event_type = kwargs['event_type']
        context['event_type'] = event_settings[
            self.event_type]['event_type']
        context['second_title'] = event_settings[
            self.event_type]['second_title']
        context['tickets'] = None
        context['volunteer_scheduling'] = event_settings[
            self.event_type]['volunteer_scheduling'] and validate_perms(
            request,
            ('Volunteer Coordinator',),
            require=False)
        return context

    def setup_ticket_links(self, request, new_event, ticket_form):
        ticket_list = ""
        for ticket_event in ticket_form.cleaned_data['ticketing_events']:
            ticket_event.linked_events.add(new_event)
            ticket_event.save()
            ticket_list = "%s - %s, %s" % (
                ticket_event.event_id,
                ticket_event.title,
                ticket_list)
        for ticket in ticket_form.cleaned_data['ticket_types']:
            ticket.linked_events.add(new_event)
            ticket.save()
            ticket_list = "%s - %s, %s" % (
                ticket.ticket_id,
                ticket.title,
                ticket_list)
        if len(ticket_list) > 0:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="LINKED_TICKETS",
                defaults={
                    'summary': "Linked New Event to Tickets",
                    'description': link_event_to_ticket_success_msg})
            messages.success(
                request,
                user_message[0].description + ticket_list)

    @method_decorator(never_cache, name="get")
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        if self.event_type == "show":
            context['second_form'] = ShowBookingForm(
                initial={'conference':  self.conference})
        else:
            context['second_form'] = GenericBookingForm(
                initial={'conference':  self.conference,
                         'type': self.event_type.title()})
        context['scheduling_form'] = ScheduleOccurrenceForm(
            conference=self.conference,
            open_to_public=True,
            initial={'duration': 1,
                     'max_volunteer': event_settings[
                        self.event_type]['max_volunteer']})
        context['worker_formset'] = self.make_formset(
            event_settings[self.event_type]['roles'])
        if validate_perms(request, ('Ticketing - Admin',), require=False):
            context['tickets'] = LinkTicketsForm(initial={
                'conference': self.conference, })
        return render(request, self.template, context)

    @method_decorator(never_cache, name="post")
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        more_view = "edit_event"
        context = self.groundwork(request, args, kwargs)
        if self.event_type == "show":
            context['second_form'] = ShowBookingForm(request.POST)
            more_view = "edit_show"
        else:
            context['second_form'] = GenericBookingForm(request.POST)
        context['scheduling_form'] = ScheduleOccurrenceForm(
            request.POST,
            conference=self.conference)
        context['worker_formset'] = self.make_formset(
            event_settings[self.event_type]['roles'],
            post=request.POST)
        if validate_perms(request, ('Ticketing - Admin',), require=False):
            context['tickets'] = LinkTicketsForm(request.POST, initial={
                'conference': self.conference, })
        if context['second_form'].is_valid(
                ) and context['scheduling_form'].is_valid(
                ) and self.is_formset_valid(context['worker_formset']) and (
                not context['tickets'] or context['tickets'].is_valid()):
            response = self.book_event(
                context['second_form'],
                context['scheduling_form'],
                context['worker_formset'],
                context['event_type'].replace(" Class",
                                              "").replace(" Event", ""))
            if context['tickets']:
                self.setup_ticket_links(request,
                                        response.occurrence,
                                        context['tickets'])
            success = self.finish_booking(
                request,
                response,
                context['scheduling_form'].cleaned_data['day'].pk)
            if success:
                if request.POST.get(
                        'set_event') == 'More...':
                    return HttpResponseRedirect(
                        "%s?volunteer_open=True&rehearsal_open=True" %
                        reverse(more_view,
                                urlconf='gbe.scheduling.urls',
                                args=[self.conference.conference_slug,
                                      response.occurrence.pk]))
                else:
                    return success
        return render(request, self.template, context)
