from django.contrib.auth.decorators import login_required
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.core.urlresolvers import reverse
from django.shortcuts import render

from gbe_logging import log_func
from gbe.functions import validate_profile
from gbe.models import Act


@login_required
@log_func
def SubmitActView(request, act_id):
    submitter = validate_profile(request, require=True)
    try:
        the_act = Act.objects.get(id=act_id)
    except Act.DoesNotExist:
        raise Http404
    if the_act not in submitter.get_acts():
        return render(request,
                      'gbe/error.tmpl',
                      {'error': "You don't own that act."})
    else:
        the_act.submitted = True
        the_act.save()
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
