from django.views.generic.list import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from gbe.models import Conference
from ticketing.models import (
    CheckListItem,
    RoleEligibilityCondition,
    TicketingEligibilityCondition,
    TicketingEvents,
    TicketItem,
)
from django.db.models import Count


class CheckListItemList(PermissionRequiredMixin, ListView):

    model = CheckListItem
    permission_required = 'ticketing.view_checklistitem'
    template_name = 'ticketing/checklistitem_list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conferences = Conference.objects.exclude(status="completed")
        role_conditions = {}
        ticket_conditions = {}
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
                ticket_conditions[condition.checklistitem][ticket] = condition
        context['ticket_conditions'] = ticket_conditions
        return context
