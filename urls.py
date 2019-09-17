# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls


urlpatterns = [
    # add your own patterns here
    url(r'^', include('gbe.urls', namespace='gbe')),
    url(r'^', include('ticketing.urls', namespace='ticketing')),
    url(r'^', include('scheduler.urls', namespace='scheduler')),
    url(r'^', include('gbe.email.urls', namespace='email')),
    url(r'^', include('gbe.reporting.urls', namespace='reporting')),
    url(r'^', include('gbe.scheduling.urls', namespace='scheduling')),
    url(r'^tinymce/', include('tinymce.urls')),
] + aldryn_addons.urls.patterns() + i18n_patterns(
    # add your own i18n patterns here
    *aldryn_addons.urls.i18n_patterns()  # MUST be the last entry!
)
