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
from gbe.models import Bio
from gbe.views.functions import (
    get_participant_form,
)


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

    troupe = get_object_or_404(Bio, resourceitem_id=troupe_id)
    # todo - goes through user model, not through scheduler IDD.  Reconsider
    if not troupe.contact.profile == profile or user.people_set.filter(
            class_name=bio.__class__.__name__, class_id=bio.pk).exists() or (
            validate_perms(request,
                           ('Registrar',
                            'Volunteer Coordinator',
                            'Act Coordinator',
                            'Vendor Coordinator',
                            'Ticketing - Admin'), require=False)):
        raise Http404
    performer_form = TroupeForm(instance=troupe,
                                prefix="The Troupe")
    performer_form.fields['membership'] = ModelMultipleChoiceField(
        queryset=troupe.membership.all())
    owner = get_participant_form(
            troupe.contact,
            prefix='Troupe Contact')
    return render(request,
                  'gbe/bid_view.tmpl',
                  {'readonlyform': [performer_form, owner]})
