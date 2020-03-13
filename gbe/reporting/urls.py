from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from gbe.reporting.views import (
    eval_view,
    interest_view,
    review_staff_area_view,
    staff_area_view,
    WelcomeLetterView,
)
from gbe.reporting import (
    download_tracks_for_show,
    env_stuff,
    export_act_techinfo,
    export_badge_report,
    list_reports,
    review_act_techinfo,
    room_schedule,
    room_setup,
    view_techinfo,
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
    url(r'^reports/review_volunteers/(?P<parent_type>area|event)/(?P<target>\d+)/?$',
        staff_area_view,
        name='staff_area'),
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
    url(r'^reports/download_tracks_for_show/(\d+)/?$',
        download_tracks_for_show,
        name='download_tracks_for_show'),

    url(r'^reports/acttechinfo/view_summary/(\d+)/?$',
        review_act_techinfo,
        name='act_techinfo_review'),
    url(r'^reports/acttechinfo/view_summary/?$',
        review_act_techinfo,
        name='act_techinfo_review'),
    url(r'^reports/acttechinfo/view_details/(\d+)/?$',
        export_act_techinfo,
        name='act_techinfo_download'),

    url(r'^reports/badges/print_run/(?P<conference_choice>[-\w]+)/?$',
        export_badge_report, name='badge_report'),
    url(r'^reports/badges/print_run/?$',
        export_badge_report, name='badge_report'),

    url(r'^reports/view_techinfo/?$',
        view_techinfo, name='view_techinfo'),
]
