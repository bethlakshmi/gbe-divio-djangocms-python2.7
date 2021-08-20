from django.views.generic.list import ListView
from django.contrib.auth.mixins import PermissionRequiredMixin
from ticketing.models import (
    CheckListItem,
    RoleEligibilityCondition,
    TicketItem,
    TicketingEvents,
)
from django.db.models import Count


class CheckListItemList(PermissionRequiredMixin, ListView):

    model = CheckListItem
    permission_required = 'ticketing.view_checklistitem'
    template_name = 'ticketing/checklistitem_list.tmpl'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tickets'] = TicketItem.objects.exclude(
            ticketing_event__conference__status="completed").exclude(
            ticketing_event__act_submission_event=True).exclude(
            ticketing_event__vendor_submission_event=True).order_by(
            'ticketing_event__title', 'title')
        context['roles'] = RoleEligibilityCondition.objects.order_by(
            'role').values_list('role', flat=True).distinct()
        context['ticket_events'] = TicketingEvents.objects.exclude(
            conference__status="completed").exclude(
            act_submission_event=True).exclude(
            vendor_submission_event=True).annotate(
            count_items=Count('ticketitems')).order_by('title')
        return context
