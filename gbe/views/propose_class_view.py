from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import (
    loader,
    RequestContext,
)
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)

from gbe_logging import log_func
from gbe.models import UserMessage
from gbe.forms import ClassProposalForm
from gbetext import (
    default_propose_submit_msg,
)


@log_func
def ProposeClassView(request):
    '''
    Handle suggestions for classes from the great unwashed
    '''
    if request.method == 'POST':
        form = ClassProposalForm(request.POST)
        user_message = UserMessage.objects.get_or_create(
            view='ProposeClassView',
            code="SUBMIT_SUCCESS",
            defaults={
                'summary': "Class Proposal Success",
                'description': default_propose_submit_msg})
        if form.is_valid():
            form.save()
            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            template = loader.get_template('gbe/class_proposal.tmpl')
            context = RequestContext(request, {'form': form})
            return HttpResponse(template.render(context))
    else:
        form = ClassProposalForm()
        template = loader.get_template('gbe/class_proposal.tmpl')
        context = RequestContext(request, {'form': form})
        return HttpResponse(template.render(context))
