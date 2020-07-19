from django.contrib.auth.decorators import login_required
from django.shortcuts import (
  get_object_or_404,
  render,
)
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.urls import reverse
from gbe_logging import log_func
from gbe.forms import ProposalPublishForm
from gbe.functions import validate_perms
from gbe.models import ClassProposal


@login_required
@log_func
def PublishProposalView(request, class_id):
    '''
    Edit an existing proposal.  This is only available to the
    proposal reviewer. The only use here is to prep and publish
    a proposal, so it's a different user community than the
    traditional "edit" thread, so it's named "publish" instead.
    '''
    page_title = "Edit Proposal"
    view_title = "Edit & Publish Proposal"
    submit_button = "Save Proposal"

    reviewer = validate_perms(request, ('Class Coordinator',))
    the_class = get_object_or_404(ClassProposal, id=class_id)

    if request.method == 'POST':
        form = ProposalPublishForm(request.POST, instance=the_class)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('proposal_review_list',
                                                urlconf='gbe.urls'))
        else:
            context = {'forms': [form],
                       'page_title': page_title,
                       'view_title': view_title,
                       'nodraft': submit_button}
    else:
        form = ProposalPublishForm(instance=the_class)
        context = {'forms': [form],
                   'page_title': page_title,
                   'view_title': view_title,
                   'nodraft': submit_button}
    return render(request, 'gbe/bid.tmpl', context)
