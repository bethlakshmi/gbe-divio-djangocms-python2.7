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
from gbe.forms import PersonaForm
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
def ViewBioView(request, id=None):
    '''
    Show troupes to troupe members, only contact should edit.
    '''
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('persona-add',
                                            urlconf='gbe.urls'))

    bio = get_object_or_404(Bio, pk=id)
    response = get_bookable_people(bio.pk, bio.__class__.__name__)
    members = []
    if len(response.people) > 0:
        members = response.people[0].users
    if not (bio.contact == profile or profile.user_object in members or
            validate_perms(request, ('Registrar',
                                     'Volunteer Coordinator',
                                     'Act Coordinator',
                                     'Vendor Coordinator',
                                     'Ticketing - Admin'), require=False)):
        raise Http404
    performer_form = PersonaForm(instance=bio, prefix='The Performer')
    owner = get_participant_form(bio.contact, prefix='The Contact')
    return render(request,
                  'gbe/bid_view.tmpl',
                  {'readonlyform': [performer_form, owner]})
