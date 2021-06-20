from django.views.decorators.cache import never_cache
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from ticketing.models import (
  Purchaser,
  Transaction,
)
from ticketing.brown_paper import process_bpt_order_list
from ticketing.eventbrite import process_eb_purchases
from django.shortcuts import render
from gbe.models import UserMessage
from gbetext import (
    import_transaction_message,
    intro_transaction_message,
)
from django.contrib.auth.models import User
from django.contrib import messages


@never_cache
def transactions(request):
    '''
    Represents the view for working with ticket items.  This will have a
    list of current ticket items, and the ability to synch them.
    '''
    validate_perms(request, ('Ticketing - Transactions', ))
    conference_choice = request.GET.get('conference', None)
    if conference_choice:
        conference = get_conference_by_slug(conference_choice)
    else:
        conference = get_current_conference()

    view_format = request.GET.get('format', 'ticket')

    intro = UserMessage.objects.get_or_create(
      view="ViewTransactions",
      code="INTRO_MESSAGE",
      defaults={'summary': "Introduction Message",
                'description': intro_transaction_message})
    count = -1
    error = ''

    if ('Sync' in request.POST):
        msgs = process_eb_purchases()
        for msg, is_success in msgs:
            if is_success:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        count = process_bpt_order_list()
        success_msg = UserMessage.objects.get_or_create(
          view="ViewTransactions",
          code="IMPORT_MESSAGE",
          defaults={
                    'summary': "Import BPT Transactions Message",
                    'description': import_transaction_message})
        messages.success(request, "%s   Transactions imported: %s - BPT" % (
            success_msg[0].description,
            count))

    user_editor = validate_perms(request, ('Registrar', ), require=False)
    context = {'conference_slugs': conference_slugs(),
               'conference': conference,
               'error': error,
               'intro': intro[0].description,
               'can_edit': user_editor,
               'view_format': view_format}
    if view_format == "ticket":
        context['transactions'] = Transaction.objects.filter(
            ticket_item__ticketing_event__conference=conference).order_by(
            'ticket_item__ticketing_event',
            'ticket_item__title',
            'purchaser')
    else:
        context['users'] = User.objects.filter(
            purchaser__transaction__ticket_item__ticketing_event__conference=conference
            ).distinct().order_by('email')
    return render(request, r'ticketing/transactions.tmpl', context)
