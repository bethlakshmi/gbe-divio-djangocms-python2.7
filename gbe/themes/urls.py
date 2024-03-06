from django.urls import re_path
from gbe.themes.views import (
    ActivateTheme,
    CloneTheme,
    DeleteTheme,
    ManageTheme,
    PreviewTheme,
    ThemeView,
    ThemesListView,
)

app_name = "themes"

urlpatterns = [
    re_path(r'^(?P<version_id>\d+)/style.css',
        ThemeView.as_view(),
        name='theme_style'),
    re_path(r'^style.css', ThemeView.as_view(), name='theme_style'),
    re_path(r'^themes/list/?',
        ThemesListView.as_view(),
        name='themes_list'),
    re_path(r'^themes/style_edit/(?P<version_id>\d+)/?',
        ManageTheme.as_view(),
        name='manage_theme'),
    re_path(r'^themes/activate/(?P<version_id>\d+)/(?P<target_system>[-\w]+)/?',
        ActivateTheme.as_view(),
        name='activate_theme'),
    re_path(r'^inventory/style_delete/(?P<version_id>\d+)/?',
        DeleteTheme.as_view(),
        name='delete_theme'),
    re_path(r'^themes/style_clone/(?P<version_id>\d+)/?',
        CloneTheme.as_view(),
        name='clone_theme'),
    re_path(r'^inventory/preview/(?P<version_id>\d+)/?',
        PreviewTheme.as_view(),
        name='preview_theme'),
    re_path(r'^inventory/preview/?',
        PreviewTheme.as_view(),
        name='preview_off'),
    ]
