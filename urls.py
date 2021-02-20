# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
from gbe.views import (
    PersonaAutocomplete,
    ProfileAutocomplete,
)


urlpatterns = [
    # add your own patterns here
    url(
        r'^persona-autocomplete/$',
        PersonaAutocomplete.as_view(),
        name='persona-autocomplete',
    ),
    url(
        r'^profile-autocomplete/$',
        ProfileAutocomplete.as_view(),
        name='profile-autocomplete',
    ),
    url(r'^', include('gbe.urls')),
    url(r'^', include('ticketing.urls')),
    url(r'^', include('gbe.email.urls')),
    url(r'^', include('gbe.reporting.urls')),
    url(r'^', include('gbe.scheduling.urls')),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
