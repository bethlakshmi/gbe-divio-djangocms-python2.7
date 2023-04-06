from django.conf.urls import url
from gbe.views import (
    ActChangeStateView,
    ActTechWizardView,
    AdminProfileView,
    ArticleCreate,
    ArticleDelete,
    ArticleDetail,
    ArticleList,
    ArticleManageList,
    ArticleUpdate,
    BiosTeachersView,
    BusinessCreate,
    BusinessUpdate,
    ClassChangeStateView,
    CloneBidView,
    CoordinateActView,
    CostumeChangeStateView,
    DeletePerformerView,
    DeleteProfileView,
    EditEmailView,
    EditProfileView,
    FashionFaireView,
    HandleUserContactEmailView,
    LandingPageView,
    MakeActView,
    MakeClassView,
    MakeCostumeView,
    MakeVendorView,
    MakeSummerActView,
    PerformerUpdate,
    PersonaCreate,
    PersonaUpdate,
    RegisterView,
    ReviewActListView,
    FlexibleReviewBidView,
    ReviewClassView,
    ReviewClassListView,
    ReviewCostumeView,
    ReviewCostumeListView,
    ReviewProfilesView,
    ReviewTroupesView,
    ReviewVendorView,
    ReviewVendorListView,
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
    CoordinatorPerformerAutocomplete,
    LimitedBusinessAutocomplete,
    LimitedPerformerAutocomplete,
    LimitedPersonaAutocomplete,
    PersonaAutocomplete,
    ProfileAutocomplete,
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
        LandingPageView.as_view(), name='home'),

    #  articles
    url(r'^news/view/(?P<slug>[-\w\d]+)', ArticleDetail.as_view(), name='news_item'),
    url(r'^news/add/$', ArticleCreate.as_view(), name='news-add'),
    url(r'^news/delete/(?P<pk>.*)/$', ArticleDelete.as_view(), name='news-delete'),
    url(r'^news/update/(?P<pk>.*)/$',
        ArticleUpdate.as_view(),
        name='news-update'),
    url(r'^news/list/?', ArticleList.as_view(), name='news_list'),
    url(r'^news/manage/?', ArticleManageList.as_view(), name='news_manage'),

    # autocompletes
    url(r'^profile-autocomplete/$',
        ProfileAutocomplete.as_view(),
        name='profile-autocomplete'),
    url(
        r'^limited-business-autocomplete/$',
        LimitedBusinessAutocomplete.as_view(),
        name='limited-business-autocomplete'),
    url(
        r'^limited-performer-autocomplete/$',
        LimitedPerformerAutocomplete.as_view(),
        name='limited-performer-autocomplete'),
    url(
        r'^limited-persona-autocomplete/$',
        LimitedPersonaAutocomplete.as_view(),
        name='limited-persona-autocomplete'),
    url(
        r'^coordinator-performer-autocomplete/$',
        CoordinatorPerformerAutocomplete.as_view(),
        name='coordinator-performer-autocomplete'),
    url(
        r'^persona-autocomplete/$',
        PersonaAutocomplete.as_view(),
        name='persona-autocomplete'),

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
    url(r'^act/coordinate/?$',
        CoordinateActView.as_view(), name='act_coord_create'),

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

    #  personae & businesses
    url(r'^troupe/view/(\d+)/?$',
        ViewTroupeView, name='troupe_view'),
    url(r'^persona/add/(?P<include_troupe>\d+)/$',
        PersonaCreate.as_view(),
        name='persona-add'),
    url(r'^persona/(?P<pk>.*)/(?P<include_troupe>\d+)/$',
        PersonaUpdate.as_view(),
        name='persona-update'),
    url(r'^performer/delete/(?P<pk>.*)/$',
        DeletePerformerView.as_view(),
        name='performer-delete'),
    url(r'^performer/(?P<pk>.*)/$',
        PerformerUpdate.as_view(),
        name='performer-update'),
    url(r'^troupe/add/$', TroupeCreate.as_view(), name='troupe-add'),
    url(r'^troupe/(?P<pk>.*)/$', TroupeUpdate.as_view(), name='troupe-update'),
    url(r'^business/add/$', BusinessCreate.as_view(), name='business-add'),
    url(r'^business/(?P<pk>.*)/$',
        BusinessUpdate.as_view(),
        name='business-update'),

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
    url(r'^accounts/register/?$',
        RegisterView.as_view(),
        name='register'),
    url(r'update_email/(?P<token>[^/]+)?$',
        EditEmailView.as_view(), name='email_update'),
    url(r'update_profile/?$',
        EditProfileView.as_view(), name='profile_update'),

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
    url(r'^profile/landing_page/(?P<profile_id>\d+)/?$',
        LandingPageView.as_view(),
        name='admin_landing_page'),
]
