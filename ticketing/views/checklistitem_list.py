from django.views.generic.list import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from gbe.models import (
    Conference,
    UserMessage
)
from ticketing.models import (
    CheckListItem,
    RoleEligibilityCondition,
    TicketingEligibilityCondition,
    TicketingEvents,
    TicketItem,
)
from django.db.models import Count
from gbetext import (
    intro_role_cond_message,
    intro_ticket_cond_message,
)


class CheckListItemList(PermissionRequiredMixin, ListView):

    model = CheckListItem
    permission_required = 'ticketing.view_checklistitem'
    template_name = 'ticketing/checklistitem_list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conferences = Conference.objects.exclude(status="completed")
        role_conditions = {}
        ticket_conditions = {}
        ticket_intro = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="TICKET_INTRO_MESSAGE",
                defaults={
                    'summary': "Ticket Condition Intro Message",
                    'description': intro_ticket_cond_message})
        role_intro = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="ROLE_INTRO_MESSAGE",
                defaults={
                    'summary': "Role Condition Intro Message",
                    'description': intro_role_cond_message})
        context['ticket_intro'] = ticket_intro[0].description
        context['role_intro'] = role_intro[0].description
        context['tickets'] = TicketItem.objects.filter(
            ticketing_event__conference__in=conferences).exclude(
            ticketing_event__act_submission_event=True).exclude(
            ticketing_event__vendor_submission_event=True).order_by(
            'ticketing_event__title', 'title')
        context['roles'] = RoleEligibilityCondition.objects.order_by(
            'role').values_list('role', flat=True).distinct()
        context['ticket_events'] = TicketingEvents.objects.filter(
            conference__in=conferences).exclude(
            act_submission_event=True).exclude(
            vendor_submission_event=True).annotate(
            count_items=Count('ticketitems')).order_by('title')
        for condition in TicketingEligibilityCondition.objects.filter(
                tickets__ticketing_event__conference__in=conferences):
            if condition.checklistitem not in ticket_conditions:
                ticket_conditions[condition.checklistitem] = {}
            for ticket in condition.tickets.all():
                if ticket.ticketing_event not in ticket_conditions[condition.checklistitem]:
                    ticket_conditions[condition.checklistitem][ticket.ticketing_event] = [ticket]
                else:
                    if ticket not in ticket_conditions[condition.checklistitem][ticket.ticketing_event]:
                        ticket_conditions[condition.checklistitem][ticket.ticketing_event] += [ticket]
        context['ticket_conditions'] = ticket_conditions

        for condition in RoleEligibilityCondition.objects.all():
            if condition.checklistitem not in role_conditions:
                role_conditions[condition.checklistitem] = {}
            role_conditions[condition.checklistitem][condition.role] = condition
        context['role_conditions'] = role_conditions

        return context
