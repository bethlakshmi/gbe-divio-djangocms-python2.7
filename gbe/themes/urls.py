from django.conf.urls import url
from gbe.themes.views import (
    ManageTheme,
    ThemeView,
)

app_name = "themes"

urlpatterns = [
    url(r'^(?P<version_id>\d+)/style.css',
        ThemeView.as_view(),
        name='theme_style'),
    url(r'^style.css', ThemeView.as_view(), name='theme_style'),
    url(r'^themes/style_edit/(?P<version_id>\d+)/?',
        ManageTheme.as_view(),
        name='manage_theme')]
