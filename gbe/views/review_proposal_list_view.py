from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

from gbe_logging import log_func
from gbe.models import (
    ClassProposal,
    Conference,
)
from gbe.functions import validate_perms


@login_required
@log_func
def ReviewProposalListView(request):
    '''
    Show the list of class bids, review results,
    and give a way to update the reviews
    '''
    reviewer = validate_perms(request, ('Class Coordinator',))
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()

    header = ClassProposal().bid_review_header
    classes = ClassProposal.objects.filter(
        conference=conference).order_by('type', 'title')
    rows = []
    for aclass in classes:
        bid_row = {}
        bid_row['bidder_active'] = True
        bid_row['bid'] = aclass.bid_review_summary
        bid_row['id'] = aclass.id
        bid_row['review_url'] = reverse('proposal_publish',
                                        urlconf='gbe.urls',
                                        args=[aclass.id])
        rows.append(bid_row)
    conference_slugs = Conference.all_slugs()
    return render(request,
                  'gbe/bid_review_list.tmpl',
                  {'header': header,
                   'rows': rows,
                   'conference': conference,
                   'conference_slugs': conference_slugs})
