from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from gbe.reporting.views import (
    act_techinfo_detail,
    eval_view,
    interest_view,
    all_volunteer_view,
    PerformerShowComp,
    review_staff_area_view,
    staff_area_view,
    WelcomeLetterView,
)
from gbe.reporting.report_views import (
    env_stuff,
    list_reports,
    room_schedule,
    room_setup,
)
from django.contrib import admin
admin.autodiscover()

app_name = "reporting"

urlpatterns = [
    url(r'^reports/?$',
        list_reports,
        name='report_list'),
    url(r'^reports/review_volunteers/?$',
        review_staff_area_view,
        name='staff_area'),
    url('^reports/review_volunteers/(?P<target>\d+)/?$',
        staff_area_view,
        name='staff_area'),
    url(r'^reports/review_all_volunteers/?$',
        all_volunteer_view,
        name='all_volunteers'),
    url(r'^reports/stuffing/(?P<conference_choice>[-\w]+)/?$',
        env_stuff,
        name='env_stuff'),
    url(r'^reports/stuffing/?$',
        env_stuff,
        name='env_stuff'),
    url(r'^reports/welcome/(?P<profile_id>\d+)/?$',
        WelcomeLetterView.as_view(),
        name='welcome_letter'),
    url(r'^reports/welcome/?$',
        WelcomeLetterView.as_view(),
        name='welcome_letter'),
    url(r'^reports/performer_comp/?$',
        PerformerShowComp.as_view(),
        name='perf_comp'),
    url(r'^reports/schedule/room/?$',
        room_schedule, name='room_schedule'),
    url(r'^reports/schedule/room/(\d+)/?$',
        room_schedule, name='room_schedule'),
    url(r'^reports/setup/room/?$',
        room_setup, name='room_setup'),
    url(r'^reports/interest/?$',
        interest_view, name='interest'),
    url(r'^reports/evaluation/?$',
        eval_view, name='evaluation'),
    url(r'^reports/evaluation/(?P<occurrence_id>\d+)/?$',
        eval_view, name='evaluation_detail'),

    url(r'^reports/acttechinfo/detail/(\d+)/?$',
        act_techinfo_detail,
        name='act_techinfo_detail'),
]
