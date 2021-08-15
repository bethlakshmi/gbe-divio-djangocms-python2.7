from ticketing.models import Transaction
from gbe.models import UserMessage
from gbetext import (
    delete_ticket_fail_message,
    delete_ticket_success_message,
)
from django.contrib import messages


def delete_ticket_item(request, view, item):
    success = False
    if Transaction.objects.filter(ticket_item=item).exists():
        error = UserMessage.objects.get_or_create(
            view=view,
            code="DELETE_FAIL",
            defaults={
                'summary': "Transactions Block Deletion",
                'description': delete_ticket_fail_message})
        messages.error(
            request,
            "%s  Ticket Item Id: %s, Title: %s" % (
                error[0].description,
                item.ticket_id,
                item.title))
    else:
        success_msg = UserMessage.objects.get_or_create(
            view=view,
            code="DELETE_SUCCESS",
            defaults={
                'summary': "Ticket Item Deleted",
                'description': delete_ticket_success_message})
        messages.success(
            request,
            "%s  Ticket Item Id: %s, Title: %s" % (
                success_msg[0].description,
                item.ticket_id,
                item.title))
        item.delete()
        success = True
    return success



def make_open_panel(ticketing_event):
    open_panel = "ticket"
    if ticketing_event.act_submission_event:
        open_panel = "act"
    elif ticketing_event.vendor_submission_event:
        open_panel = "vendor"
    return open_panel
