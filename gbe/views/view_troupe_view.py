from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.forms import ModelMultipleChoiceField
from gbe_logging import log_func
from gbe.forms import TroupeForm
from gbe.functions import (
    validate_perms,
    validate_profile,
)
from gbe.models import (
    Bio,
    Profile,
)
from gbe.views.functions import (
    get_participant_form,
)
from scheduler.idd import get_bookable_people


@login_required
@log_func
def ViewTroupeView(request, troupe_id=None):
    '''
    Show troupes to troupe members, only contact should edit.
    '''
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('troupe-add',
                                            urlconf='gbe.urls'))

    troupe = get_object_or_404(Bio, pk=troupe_id)
    response = get_bookable_people(troupe.pk, troupe.__class__.__name__)
    if not (troupe.contact == profile or (
            profile.user_object in response.people[0].users) or validate_perms(
            request, ('Registrar',
                      'Volunteer Coordinator',
                      'Act Coordinator',
                      'Vendor Coordinator',
                      'Ticketing - Admin'), require=False)):
        raise Http404
    user_ids = [user.pk for user in response.people[0].users]
    performer_form = TroupeForm(instance=troupe,
                                prefix="The Troupe")
    performer_form.fields['membership'] = ModelMultipleChoiceField(
        queryset=Profile.objects.filter(user_object__pk__in=user_ids))
    owner = get_participant_form(
            troupe.contact,
            prefix='Troupe Contact')
    return render(request,
                  'gbe/bid_view.tmpl',
                  {'readonlyform': [performer_form, owner]})
