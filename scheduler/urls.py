from django.conf.urls import url
from django.contrib.auth.views import *
from scheduler import views

app_name = "scheduler"

urlpatterns = [
    url(r'^scheduler/export_calendar/?$',
        views.export_calendar, name='export_calendar'),
]
