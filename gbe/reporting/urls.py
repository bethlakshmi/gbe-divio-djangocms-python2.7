from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.conf.urls.static import static
from gbe.reporting.views import (
    act_techinfo_detail,
    ActTechList,
    eval_view,
    interest_view,
    all_volunteer_view,
    PerformerSlidesList,
    PerformerShowComp,
    review_staff_area_view,
    RoomScheduleView,
    staff_area_view,
    ShowSlidesView,
    UserPrivView,
    WelcomeLetterView,
)
from gbe.reporting.report_views import (
    env_stuff,
    list_reports,
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
    url(r'^reports/show_slide_list/?$',
        ShowSlidesView.as_view(),
        name='show_slide_list'),
    url(r'^reports/schedule/room/?$',
        RoomScheduleView.as_view(), name='room_schedule'),
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
    url(r'^reports/act_tech_list/(?P<occurrence_id>\d+)/?$',
        ActTechList.as_view(),
        name='act_tech_list'),
    url(r'^reports/performer_urls/(?P<occurrence_id>\d+)/?$',
        PerformerSlidesList.as_view(),
        name='performer_urls'),
    url(r'^reports/privileges/?$',
        staff_member_required(UserPrivView.as_view()),
        name='user_privs'),
]
