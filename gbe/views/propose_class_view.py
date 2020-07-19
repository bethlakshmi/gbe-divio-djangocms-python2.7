from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)

from gbe_logging import log_func
from gbe.models import (
    Conference,
    UserMessage,
)
from gbe.forms import ClassProposalForm
from gbetext import (
    default_propose_submit_msg,
)
from django.shortcuts import render


@log_func
def ProposeClassView(request):
    '''
    Handle suggestions for classes from the great unwashed
    '''
    context = {}
    if request.method == 'POST':
        form = ClassProposalForm(request.POST)
        user_message = UserMessage.objects.get_or_create(
            view='ProposeClassView',
            code="SUBMIT_SUCCESS",
            defaults={
                'summary': "Class Proposal Success",
                'description': default_propose_submit_msg})
        if form.is_valid():
            proposal = form.save()
            proposal.conference = Conference.objects.filter(
                    accepting_bids=True).first()
            proposal.save()
            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            context = {'form': form}
    else:
        form = ClassProposalForm()
        context = {'form': form}
    return render(request, 'gbe/class_proposal.tmpl', context)
