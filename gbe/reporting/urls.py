from django.urls import re_path
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.conf.urls.static import static
from gbe.reporting.views import (
    ActTechInfoDetail,
    ActTechList,
    AllVolunteerView,
    EnvStuffView,
    EvalView,
    InterestView,
    PerformerSlidesList,
    PerformerShowComp,
    ReviewStaffAreaarView,
    RoomScheduleView,
    RoomSetupView,
    StaffAreaView,
    ShowSlidesView,
    UserPrivView,
    VendorHistory,
    WelcomeLetterView,
)
from django.contrib import admin
admin.autodiscover()

app_name = "reporting"

urlpatterns = [
    re_path(r'^reports/review_volunteers/?$',
            ReviewStaffAreaarView.as_view(),
            name='staff_area'),
    re_path('^reports/review_volunteers/(?P<pk>\d+)/?$',
            StaffAreaView.as_view(),
            name='staff_area'),
    re_path(r'^reports/review_all_volunteers/?$',
            AllVolunteerView.as_view(),
            name='all_volunteers'),
    re_path(r'^reports/stuffing/?$',
            EnvStuffView.as_view(),
            name='env_stuff'),
    re_path(r'^reports/welcome/(?P<profile_id>\d+)/?$',
            WelcomeLetterView.as_view(),
            name='welcome_letter'),
    re_path(r'^reports/welcome/?$',
            WelcomeLetterView.as_view(),
            name='welcome_letter'),
    re_path(r'^reports/performer_comp/?$',
            PerformerShowComp.as_view(),
            name='perf_comp'),
    re_path(r'^reports/show_slide_list/?$',
            ShowSlidesView.as_view(),
            name='show_slide_list'),
    re_path(r'^reports/schedule/room/?$',
            RoomScheduleView.as_view(),
            name='room_schedule'),
    re_path(r'^reports/setup/room/?$',
            RoomSetupView.as_view(),
            name='room_setup'),
    re_path(r'^reports/interest/?$',
            InterestView.as_view(),
            name='interest'),
    re_path(r'^reports/evaluation/?$',
            EvalView.as_view(),
            name='evaluation'),
    re_path(r'^reports/evaluation/(?P<occurrence_id>\d+)/?$',
            EvalView.as_view(),
            name='evaluation_detail'),

    re_path(r'^reports/acttechinfo/detail/(?P<pk>\d+)/?$',
            ActTechInfoDetail.as_view(),
            name='act_techinfo_detail'),
    re_path(r'^reports/act_tech_list/(?P<occurrence_id>\d+)/?$',
            ActTechList.as_view(),
            name='act_tech_list'),
    re_path(r'^reports/performer_urls/(?P<occurrence_id>\d+)/?$',
            PerformerSlidesList.as_view(),
            name='performer_urls'),
    re_path(r'^reports/privileges/?$',
            staff_member_required(UserPrivView.as_view()),
            name='user_privs'),
    re_path(r'^reports/vendors_over_time/?$',
            VendorHistory.as_view(),
            name='vendor_history'),
]
