from django.conf.urls import url
from django.contrib.auth.views import (
    LoginView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from gbe.views import (
    ActChangeStateView,
    ActTechWizardView,
    AdminProfileView,
    BiosTeachersView,
    ClassChangeStateView,
    CloneBidView,
    ConferenceVolunteerView,
    CostumeChangeStateView,
    DeleteProfileView,
    EditEmailView,
    EditPersonaView,
    EditProfileView,
    EditTroupeView,
    FashionFaireView,
    HandleUserContactEmailView,
    LandingPageView,
    LogoutView,
    MakeActView,
    MakeClassView,
    MakeCostumeView,
    MakeVendorView,
    MakeVolunteerView,
    MakeSummerActView,
    PerformerUpdate,
    PersonaCreate,
    PersonaUpdate,
    ProposeClassView,
    PublishProposalView,
    RegisterView,
    RegisterPersonaView,
    ReviewActListView,
    FlexibleReviewBidView,
    ReviewClassView,
    ReviewClassListView,
    ReviewCostumeView,
    ReviewCostumeListView,
    ReviewProfilesView,
    ReviewProposalListView,
    ReviewTroupesView,
    ReviewVendorView,
    ReviewVendorListView,
    ReviewVolunteerView,
    ReviewVolunteerListView,
    SubmitActView,
    TroupeCreate,
    TroupeUpdate,
    VendorChangeStateView,
    ViewActView,
    ViewClassView,
    ViewCostumeView,
    ViewSummerActView,
    ViewTroupeView,
    ViewVendorView,
    ViewVolunteerView,
)

# NOTE: in general, url patterns should end with '/?$'. This
# means "match the preceding pattern, plus an optional final '?',
# and no other characters following. So '^foo/?$' matches on
# "foo" or "foo/", but not on "foo/bar" or "foo!".
# Which is what we usually want.
app_name = "gbe"

urlpatterns = [
    #  landing page
    url(r'^gbe/?',
        LandingPageView, name='home'),

    #  bios
    url(r'^bios/teachers/?$',
        BiosTeachersView, name='bios_teacher'),

    #  acts
    url(r'^act/create/?$',
        MakeActView.as_view(), name='act_create'),
    url(r'^act/edit/(?P<bid_id>\d+)/?$',
        MakeActView.as_view(), name='act_edit'),
    url(r'^act/view/(?P<bid_id>\d+)/?$',
        ViewActView.as_view(), name='act_view'),
    url(r'^act/review/(?P<object_id>\d+)/?$',
        FlexibleReviewBidView.as_view(), name='act_review'),
    url(r'^act/review/?$',
        ReviewActListView.as_view(), name='act_review'),
    url(r'^act/reviewlist/?$',
        ReviewActListView.as_view(),
        name='act_review_list'),
    url(r'^act/submit/(\d+)/?$',
        SubmitActView, name='act_submit'),
    url(r'^act/changestate/(?P<object_id>\d+)/?$',
        ActChangeStateView.as_view(),
        name='act_changestate'),

    url(r'^summer_act/create/?$',
        MakeSummerActView.as_view(), name='summeract_create'),
    url(r'^summer_act/edit/(?P<bid_id>\d+)/?$',
        MakeSummerActView.as_view(), name='summeract_edit'),
    url(r'^summer_act/view/(?P<bid_id>\d+)/?$',
        ViewSummerActView.as_view(), name='summeract_view'),

    #  act tech info - delete act_techinfo_edit after GBE 2020
    url(r'^acttechinfo/edit/(\d+)/?$',
        ActTechWizardView.as_view(),
        name='act_techinfo_edit'),
    url(r'^acttechinfo/wizard/(?P<act_id>\d+)/?$',
        ActTechWizardView.as_view(),
        name='act_tech_wizard'),

    #  classes
    url(r'^class/create/?$',
        MakeClassView.as_view(), name='class_create'),
    url(r'class/edit/(?P<bid_id>\d+)/?$',
        MakeClassView.as_view(), name='class_edit'),
    url(r'^class/view/(?P<bid_id>\d+)/?$',
        ViewClassView.as_view(), name='class_view'),
    url(r'^class/review/(?P<object_id>\d+)/?$',
        ReviewClassView.as_view(), name='class_review'),
    url(r'^class/review/?$',
        ReviewClassListView.as_view(), name='class_review'),
    url(r'^class/reviewlist/?$',
        ReviewClassListView.as_view(), name='class_review_list'),
    url(r'^class/changestate/(?P<object_id>\d+)/?$',
        ClassChangeStateView.as_view(),
        name='class_changestate'),

    #  proposals
    url(r'^class/propose/?$',
        ProposeClassView,
        name='class_propose'),
    url(r'^classpropose/edit/?$',
        PublishProposalView,
        name='proposal_publish'),
    url(r'^classpropose/edit/(\d+)/?$',
        PublishProposalView,
        name='proposal_publish'),
    url(r'^classpropose/reviewlist/?$',
        ReviewProposalListView,
        name='proposal_review_list'),

    #  conference
    url(r'^conference/volunteer/?$',
        ConferenceVolunteerView,
        name='conference_volunteer'),

    #  personae
    url(r'^performer/create/?$',
        RegisterPersonaView, name='persona_create'),
    url(r'^persona/edit/(\d+)/?$',
        EditPersonaView, name='persona_edit'),
    url(r'^troupe/create/?$',
        EditTroupeView, name='troupe_create'),
    url(r'^troupe/edit/(\d+)/?$',
        EditTroupeView, name='troupe_edit'),
    url(r'^troupe/view/(\d+)/?$',
        ViewTroupeView, name='troupe_view'),
    url(r'^persona/add/(?P<include_troupe>\d+)/$',
        PersonaCreate.as_view(),
        name='persona-add'),
    url(r'^persona/(?P<pk>.*)/(?P<include_troupe>\d+)/$',
        PersonaUpdate.as_view(),
        name='persona-update'),
    url(r'^performer/(?P<pk>.*)/$',
        PerformerUpdate.as_view(),
        name='performer-update'),
    url(r'^troupe/add/$', TroupeCreate.as_view(), name='troupe-add'),
    url(r'^troupe/(?P<pk>.*)/$', TroupeUpdate.as_view(), name='troupe-update'),

    #  volunteers
    url(r'^volunteer/view/(?P<bid_id>\d+)/?$',
        ViewVolunteerView.as_view(), name='volunteer_view'),
    url(r'^volunteer/edit/(?P<bid_id>\d+)/?$',
        MakeVolunteerView.as_view(), name='volunteer_edit'),
    url(r'^volunteer/review/(?P<object_id>\d+)/?$',
        ReviewVolunteerView.as_view(), name='volunteer_review'),
    url(r'^volunteer/review/?$',
        ReviewVolunteerListView.as_view(),
        name='volunteer_review'),
    url(r'^volunteer/reviewlist/?$',
        ReviewVolunteerListView.as_view(),
        name='volunteer_review_list'),

    #  vendors
    url(r'^vendor/create/?$',
        MakeVendorView.as_view(), name='vendor_create'),
    url(r'^vendor/edit/(?P<bid_id>\d+)/?$',
        MakeVendorView.as_view(), name='vendor_edit'),
    url(r'^vendor/view/(?P<bid_id>\d+)/?$',
        ViewVendorView.as_view(), name='vendor_view'),
    url(r'^vendor/review/(?P<object_id>\d+)/?$',
        ReviewVendorView.as_view(), name='vendor_review'),
    url(r'^vendor/review/?$',
        ReviewVendorListView.as_view(),
        name='vendor_review'),
    url(r'^vendor/reviewlist/?$',
        ReviewVendorListView.as_view(),
        name='vendor_review_list'),
    url(r'^vendor/changestate/(?P<object_id>\d+)/?$',
        VendorChangeStateView.as_view(),
        name='vendor_changestate'),

    #  costumes
    url(r'^costume/create/?$',
        MakeCostumeView.as_view(), name='costume_create'),
    url(r'costume/edit/(?P<bid_id>\d+)/?$',
        MakeCostumeView.as_view(), name='costume_edit'),
    url(r'^costume/view/(?P<bid_id>\d+)/?$',
        ViewCostumeView.as_view(), name='costume_view'),
    url(r'^costume/review/(?P<object_id>\d+)/?$',
        ReviewCostumeView.as_view(), name='costume_review'),
    url(r'^costume/review/?$',
        ReviewCostumeListView.as_view(), name='costume_review'),
    url(r'^costume/reviewlist/?$',
        ReviewCostumeListView.as_view(), name='costume_review_list'),
    url(r'^costume/changestate/(?P<object_id>\d+)/?$',
        CostumeChangeStateView.as_view(),
        name='costume_changestate'),

    url(r'^clone/(?P<bid_type>\w+)/(?P<bid_id>\d+)/?$',
        CloneBidView,
        name='clone_bid'),

    #  miscellaneous URLs
    url(r'^fashion_faire/$',
        FashionFaireView, name='fashion_faire'),

    #  site utility stuff
    url(r'^login/?$',
        LoginView.as_view(),
        name='login'),
    url(r'^logout/?$',
        LogoutView, name='logout'),
    url(r'^accounts/login/?$',
        LoginView.as_view()),
    url(r'^accounts/logout/?$', LogoutView),
    url(r'^accounts/register/?$',
        RegisterView, name='register'),
    url(r'update_email/(?P<token>[^/]+)?$',
        EditEmailView.as_view(), name='email_update'),
    url(r'update_profile/?$',
        EditProfileView.as_view(), name='profile_update'),

    #  password reset
    url(r'^accounts/password/reset/?$',
        PasswordResetView.as_view(
            success_url='/accounts/password/reset/done/'),
        name="password_reset"),
    url(r'^accounts/password/reset/done/?$',
        PasswordResetDoneView.as_view(),
        name='password_reset_done'),
    url(r'^accounts/password/confirm/'
        r'(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$',
        PasswordResetConfirmView.as_view(
            success_url='/accounts/password/reset/complete/'),
        name="password_reset_confirm"),
    url(r'^accounts/password/reset/complete/?$',
        PasswordResetCompleteView.as_view()),

    #  registration & user management
    url(r'^user_contact/?$',
        HandleUserContactEmailView,
        name='handle_user_contact_email'),
    url(r'^profile/manage/?$',
        ReviewProfilesView,
        name='manage_users'),
    url(r'^troupe/manage/?$',
        ReviewTroupesView.as_view(),
        name='manage_troupes'),
    url(r'^profile/admin/(?P<profile_id>\d+)/?$',
        AdminProfileView.as_view(),
        name='admin_profile'),
    url(r'^profile/delete/(\d+)/?$',
        DeleteProfileView,
        name='delete_profile'),
    url(r'^profile/landing_page/(\d+)/?$',
        LandingPageView,
        name='admin_landing_page')
]
