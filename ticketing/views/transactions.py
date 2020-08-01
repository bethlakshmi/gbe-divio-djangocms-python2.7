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
from ticketing.brown_paper import get_bpt_last_poll_time
from django.shortcuts import render
from gbe.models import UserMessage
from gbetext import intro_transaction_message
from django.contrib.auth.models  import User

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
                defaults={
                    'summary': "Introduction Message",
                    'description': intro_transaction_message})
    count = -1
    error = ''

    if ('Sync' in request.POST):
        count = process_bpt_order_list()

    sync_time = get_bpt_last_poll_time()

    user_editor = validate_perms(request, ('Registrar', ), require=False)
    context = {'conference_slugs': conference_slugs(),
               'conference': conference,
               'sync_time': sync_time,
               'error': error,
               'count': count,
               'intro': intro[0].description,
               'can_edit': user_editor,
               'view_format': view_format}
    if view_format == "ticket":
        context['transactions'] = Transaction.objects.filter(
            ticket_item__bpt_event__conference=conference).order_by(
            'ticket_item__bpt_event',
            'ticket_item__title',
            'purchaser')
    else:
        context['users'] = User.objects.filter(
            purchaser__transaction__ticket_item__bpt_event__conference=conference
            ).distinct().order_by('email')
    return render(request, r'ticketing/transactions.tmpl', context)
