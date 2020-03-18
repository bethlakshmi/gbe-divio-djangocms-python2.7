from django.conf.urls import url

from gbe.email.views import (
    EditTemplateView,
    ListTemplateView,
    MailToBiddersView,
    MailToPersonView,
    MailToRolesView,
)

# NOTE: in general, url patterns should end with '/?$'. This
# means "match the preceding patter, plus an optional final '?',
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!".
# Which is what we usually want.

app_name = "email"

urlpatterns = [
    url(r'^email/edit_template/(?P<template_name>[\w|\W]+)/?$',
        EditTemplateView.as_view(), name='edit_template'),
    url(r'^email/list_template/?$',
        ListTemplateView.as_view(), name='list_template'),
    url(r'^email/mail_to_bidders/?$',
        MailToBiddersView.as_view(), name='mail_to_bidders'),
    url(r'^email/mail_to_individual/(?P<profile_id>\d+)?$',
        MailToPersonView.as_view(), name='mail_to_individual'),
    url(r'^email/mail_to_roles/?$',
        MailToRolesView.as_view(), name='mail_to_roles'),
]
