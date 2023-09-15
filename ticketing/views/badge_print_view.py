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
from gbe.functions import get_latest_conference
from scheduler.idd import get_people


class BadgePrintView(PermissionRequiredMixin, View):

    permission_required = 'ticketing.view_transaction'

    @never_cache
    def get(self, request):
        conference = get_latest_conference()
        badged_usernames = []

        badged_purchases = Transaction.objects.filter(
            ticket_item__ticketing_event__conference=conference).exclude(
            ticket_item__ticketingeligibilitycondition__checklistitem__badge_title__isnull=True
            ).order_by('ticket_item')

        header = ['First',
                  'Last',
                  'username',
                  'Badge Name',
                  'Badge Type',
                  'Ticket Purchased',
                  'Date']

        badge_info = []
        # now build content - the order of loops is specific here,
        # we need ALL transactions, if they are limbo, then the purchaser
        # should have a BPT first/last name
        for badge in badged_purchases:
            buyer = badge.purchaser.matched_to_user
            badged_usernames += [buyer.username]
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
                     badge.import_date])

        role_conditions = RoleEligibilityCondition.objects.exclude(
            checklistitem__badge_title__isnull=True)
        title_to_badge = {}
        if role_conditions.count() > 0:
            for role_cond in role_conditions:
                title_to_badge[
                    role_cond.role] = role_cond.checklistitem.badge_title
            roles = role_conditions.values_list('role', flat=True).distinct()
            response = get_people(labels=[conference.conference_slug],
                                  roles=roles)

            for people in response.people:
                for user in people.users:
                    if user.username not in badged_usernames:
                        badge_info.append(
                            [user.first_name,
                             user.last_name,
                             user.username,
                             user.profile.get_badge_name(),
                             title_to_badge[people.role],
                             "Role Condition: %s" % people.role,
                             "N/A"])
                        badged_usernames += [user.username]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=print_badges.csv'
        writer = csv.writer(response)
        writer.writerow(header)
        for row in badge_info:
            writer.writerow(row)
        return response
