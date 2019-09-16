from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from gbe_logging import log_func
from gbe.forms import ComboForm


@login_required
@log_func
def CreateComboView(request):
    page_title = 'Manage Combo'
    view_title = 'Who is in this Combo?'
    submit_button = 'Save Combo'

    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('combo_create',
                                            urlconf='gbe.urls'))
    if not profile.personae.exists():
        return HttpResponseRedirect(reverse('persona_create',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('combo_create',
                                            urlconf='gbe.urls'))
    if request.method == 'POST':
        form = ComboForm(request.POST, request.FILES)
        if form.is_valid():
            troupe = form.save(commit=True)
            troupe_id = troupe.pk
            return HttpResponseRedirect(reverse('home'), urlconf='gbe.urls')
        else:
            return render(request, 'gbe/bid.tmpl',
                          {'forms': [form],
                           'nodraft': submit_button,
                           'page_title': page_title,
                           'view_title': view_title,
                           'view_header_text': combo_header_text})
    else:
        form = ComboForm(initial={'contact': profile})
        return render(request, 'gbe/bid.tmpl',
                      {'forms': [form],
                       'nodraft': submit_button,
                       'page_title': page_title,
                       'view_title': view_title,
                       'view_header_text': combo_header_text})
