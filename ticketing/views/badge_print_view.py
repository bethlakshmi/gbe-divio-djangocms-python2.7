from django.views.generic import View
from django.contrib.auth.mixins import PermissionRequiredMixin
from ticketing.models import (
    CheckListItem,
    RoleEligibilityCondition,
    TicketingEligibilityCondition,
    TicketingEvents,
    TicketItem,
    Transaction,
)
from django.http import HttpResponse
import csv
from django.views.decorators.cache import never_cache


class BadgePrintView(PermissionRequiredMixin, View):

    permission_required = 'ticketing.view_transaction'

    @never_cache
    def get(self, request):
        badges = Transaction.objects.exclude(
            ticket_item__ticketingeligibilitycondition__checklistitem__badge_title__isnull=True
            ).exclude(
            ticket_item__ticketing_event__conference__status='completed'
            ).order_by('ticket_item')

        header = ['First',
                  'Last',
                  'username',
                  'Badge Name',
                  'Badge Type',
                  'Ticket Purhased',
                  'Date',
                  'State']

        badge_info = []
        # now build content - the order of loops is specific here,
        # we need ALL transactions, if they are limbo, then the purchaser
        # should have a BPT first/last name
        for badge in badges:
            buyer = badge.purchaser.matched_to_user
            if hasattr(buyer, 'profile') and len(
                    buyer.profile.get_badge_name()) > 0:
                badge_name = buyer.profile.get_badge_name()
            else:
                badge_name = badge.purchaser.first_name
            for condition in badge.ticket_item.ticketingeligibilitycondition_set.exclude(
                    checklistitem__badge_title__isnull=True):
                badge_info.append(
                    [badge.purchaser.first_name,
                     badge.purchaser.last_name,
                     buyer.username,
                     str(badge_name),
                     condition.checklistitem.badge_title,
                     badge.ticket_item.title,
                     badge.import_date,
                     'In GBE'])

        # end for loop through acts
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=print_badges.csv'
        writer = csv.writer(response)
        writer.writerow(header)
        for row in badge_info:
            writer.writerow(row)
        return response
