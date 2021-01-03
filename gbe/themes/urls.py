from django.conf.urls import url
from gbe.themes.views import (
    ActivateTheme,
    ManageTheme,
    ThemeView,
    ThemesListView,
)

app_name = "themes"

urlpatterns = [
    url(r'^(?P<version_id>\d+)/style.css',
        ThemeView.as_view(),
        name='theme_style'),
    url(r'^style.css', ThemeView.as_view(), name='theme_style'),
    url(r'^themes/list/?',
        ThemesListView.as_view(),
        name='themes_list'),
    url(r'^themes/style_edit/(?P<version_id>\d+)/?',
        ManageTheme.as_view(),
        name='manage_theme'),
    url(r'^themes/activate/(?P<version_id>\d+)/(?P<target_system>[-\w]+)/?',
        ActivateTheme.as_view(),
        name='activate_theme'),
    ]
