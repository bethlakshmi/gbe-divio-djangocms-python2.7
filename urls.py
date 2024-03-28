# -*- coding: utf-8 -*-
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
from gbe.views import (
    CoordinatorPerformerAutocomplete,
    LimitedBusinessAutocomplete,
    LimitedPerformerAutocomplete,
    LimitedPersonaAutocomplete,
    PersonaAutocomplete,
    ProfileAutocomplete,
)
# import debug_toolbar
from django.urls import include, path, re_path


urlpatterns = [
    # add your own patterns here
    path('accounts/', include('django.contrib.auth.urls')),
    re_path(r'^', include('gbe.urls')),
    re_path(r'^', include('ticketing.urls')),
    re_path(r'^', include('gbe.email.urls')),
    re_path(r'^', include('gbe.reporting.urls')),
    re_path(r'^', include('gbe.scheduling.urls')),
    re_path(r'^', include('gbe.themes.urls')),
    re_path(r'^paypal/', include('paypal.standard.ipn.urls')),
    #    path('__debug__/', include(debug_toolbar.urls)),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
