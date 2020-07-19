from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from gbe_logging import log_func
from gbe.models import Persona
from gbe.forms import PersonaForm
from gbe.functions import validate_profile
from gbetext import default_edit_persona_msg
from gbe.models import UserMessage


@login_required
@log_func
@never_cache
def EditPersonaView(request, persona_id):
    '''
    Modify an existing Persona object.
    '''
    page_title = 'Manage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    submit_button = 'Save Persona'
    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls'))
    persona = get_object_or_404(Persona, resourceitem_id=persona_id)
    if persona.performer_profile != profile:
        raise PermissionDenied

    if request.method == 'POST':
        form = PersonaForm(request.POST,
                           request.FILES,
                           instance=persona)
        if form.is_valid():
            performer = form.save(commit=True)
            user_message = UserMessage.objects.get_or_create(
                view='EditPersonaView',
                code="UPDATE_PERSONA",
                defaults={
                    'summary': "Create Persona Success",
                    'description': default_edit_persona_msg})
            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home',
                                                urlconf='gbe.urls'))
        else:
            return render(request,
                          'gbe/bid.tmpl',
                          {'forms': [form],
                           'nodraft': submit_button,
                           'page_title': page_title,
                           'view_title': view_title,
                           })
    else:
        form = PersonaForm(instance=persona)
        return render(request,
                      'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title': view_title,
                       })
