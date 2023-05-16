# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls

# import debug_toolbar
from django.urls import include, path


urlpatterns = [
    # add your own patterns here
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^', include('gbe.urls')),
    url(r'^', include('ticketing.urls')),
    url(r'^', include('gbe.email.urls')),
    url(r'^', include('gbe.reporting.urls')),
    url(r'^', include('gbe.scheduling.urls')),
    url(r'^', include('gbe.themes.urls')),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    #    path('__debug__/', include(debug_toolbar.urls)),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
