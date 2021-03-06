# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
from gbe.views import (
    LimitedBusinessAutocomplete,
    LimitedPerformerAutocomplete,
    LimitedPersonaAutocomplete,
    PersonaAutocomplete,
    ProfileAutocomplete,
)


urlpatterns = [
    # add your own patterns here
    url(
        r'^limited-business-autocomplete/$',
        LimitedBusinessAutocomplete.as_view(),
        name='limited-business-autocomplete',
    ),
    url(
        r'^limited-performer-autocomplete/$',
        LimitedPerformerAutocomplete.as_view(),
        name='limited-performer-autocomplete',
    ),
    url(
        r'^limited-persona-autocomplete/$',
        LimitedPersonaAutocomplete.as_view(),
        name='limited-persona-autocomplete',
    ),
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
    url(r'^', include('gbe.themes.urls')),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
