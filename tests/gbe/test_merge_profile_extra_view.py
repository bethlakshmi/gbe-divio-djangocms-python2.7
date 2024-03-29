from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group, User
from tests.factories.gbe_factories import (
    ActFactory,
    ActBidEvaluationFactory,
    ArticleFactory,
    BidEvaluationFactory,
    BioFactory,
    ClassFactory,
    CostumeFactory,
    FlexibleEvaluationFactory,
    ProfileFactory,
    VendorFactory,
)
from tests.factories.ticketing_factories import PurchaserFactory
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import warn_user_merge_delete_2
from gbe.models import (
    Act,
    ActBidEvaluation,
    Article,
    BidEvaluation,
    Bio,
    Business,
    Class,
    Costume,
    FlexibleEvaluation,
    Profile,
    StaffArea,
    Vendor,
)
from scheduler.models import (
    EventEvalGrade,
    PeopleAllocation,
)
from ticketing.models import Purchaser
from settings import GBE_DATETIME_FORMAT
from mock import patch
from scheduler.data_transfer import (
    ScheduleResponse,
    ScheduleItem,
)
from gbe.forms import BidBioMergeForm


class TestMergeProfileExtra(TestCase):
    '''Tests for admin_profile  view'''
    view_name = 'merge_bios'
    counter = 0

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Registrar')

    def setUp(self):
        self.profile = ProfileFactory()
        self.avail_profile = ProfileFactory()
        self.url = reverse(self.view_name,
                           urlconf='gbe.urls',
                           args=[self.profile.pk, self.avail_profile.pk])

    def test_no_privilege(self):
        random_user = ProfileFactory().user_object
        login_as(random_user, self)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_error_on_self(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf='gbe.urls',
                    args=[self.profile.pk, self.privileged_user.profile.pk]),
            follow=True)
        self.assertContains(response, warn_user_merge_delete_2)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_get_form_w_bios(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        target_bio = BioFactory(contact=self.profile)
        avail_bio = BioFactory(contact=self.avail_profile)
        act = ActFactory(bio__contact=self.profile)
        klass = ClassFactory(teacher_bio__contact=self.avail_profile)
        costume = CostumeFactory(profile=self.profile,
                                 bio=act.bio)
        response = self.client.get(self.url)
        self.assertContains(response, 'Merge Users - Merge Bios')
        self.assertContains(response, avail_bio.name)
        self.assertContains(response, "%s - %s: %s" % (
            act.b_conference.conference_slug,
            act.__class__.__name__,
            act.b_title))
        self.assertContains(response, "%s - %s: %s" % (
            klass.b_conference.conference_slug,
            klass.__class__.__name__,
            klass.b_title))
        self.assertContains(response, "%s - %s: %s" % (
            costume.b_conference.conference_slug,
            costume.__class__.__name__,
            costume.b_title))
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (target_bio.pk,
                                                target_bio.name),
            html=True)

    def test_bad_form_setup(self):
        msg = "no message"
        try:
            form = BidBioMergeForm(initial={"stuff": "random"})
        except Exception as e:
            msg = e.args[0]
        self.assertEqual(msg, "Intial with two profiles are required")

    def test_get_form_w_business(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        vendor = VendorFactory()
        avail_vendor = VendorFactory()
        vendor.business.owners.add(self.profile)
        avail_vendor.business.owners.add(self.avail_profile)
        response = self.client.get(self.url)
        self.assertContains(response, 'Merge Users - Merge Bios')
        self.assertContains(response, avail_vendor.business.name)
        self.assertContains(response, "%s - %s: %s" % (
            vendor.b_conference.conference_slug,
            vendor.__class__.__name__,
            str(vendor)))
        self.assertContains(response, "%s - %s: %s" % (
            avail_vendor.b_conference.conference_slug,
            avail_vendor.__class__.__name__,
            str(avail_vendor)))
        self.assertContains(
            response,
            '<option value="%d">%s</option>' % (vendor.business.pk,
                                                vendor.business.name),
            html=True)

    def test_get_form_w_staff_lead(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        context = StaffAreaContext(staff_lead=self.profile)
        response = self.client.get(self.url)
        self.assertContains(response, 'Merge Users - Merge Bios')
        self.assertContains(response, "%s - %s" % (
            context.conference.conference_slug,
            context.area.title))
        self.assertContains(response, "Staff Lead")

    def test_get_form_w_privs(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        grant_privilege(self.profile, "Act Coordinator")
        response = self.client.get(self.url)
        self.assertContains(response, 'Merge Users - Merge Bios')
        self.assertContains(response, "Act Coordinator")

    def test_move_bids_submit(self):
        login_as(self.privileged_user, self)
        target_bio = BioFactory(contact=self.profile)
        avail_bio = BioFactory(contact=self.avail_profile)
        act = ActFactory(bio=avail_bio)
        costume = CostumeFactory(profile=self.avail_profile, bio=avail_bio)
        response = self.client.post(self.url, data={
            "bio_%d" % avail_bio.pk: target_bio.pk}, follow=True)
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertFalse(Bio.objects.filter(pk=avail_bio.pk).exists())
        self.assertContains(response, "Sucessfully deleted profile %s." % (
            self.avail_profile.get_badge_name()))
        self.assertContains(
            response,
            "Sucessfully deleted bio %s for profile %s." % (
                avail_bio.name,
                self.avail_profile.get_badge_name()))
        self.assertTrue(Act.objects.filter(bio__pk=target_bio.pk,
                                           pk=act.pk).exists)
        self.assertTrue(
            Costume.objects.filter(profile__pk=self.profile.pk,
                                   bio__pk=target_bio.pk,
                                   pk=costume.pk).exists())

    def test_move_bids_invalid_bio(self):
        login_as(self.privileged_user, self)
        target_bio = BioFactory(contact=self.profile)
        avail_bio = BioFactory(contact=self.avail_profile)
        invalid_bio = BioFactory()
        act = ActFactory(bio=avail_bio)
        response = self.client.post(self.url, data={
            "bio_%d" % avail_bio.pk: invalid_bio.pk}, follow=True)
        self.assertContains(
            response,
            ("Select a valid choice. %d is not one of the available " +
             "choices.") % invalid_bio.pk)

    def test_move_bio_booked_troupe_act_submit(self):
        # Extra setup to make this a troupe that is shared by both
        # profiles.  Merge removes the extra profile, leaving a troupe of 1
        login_as(self.privileged_user, self)
        avail_bio = BioFactory(contact=self.avail_profile,
                               multiple_performers=True)
        context = ShowContext(performer=avail_bio)
        context.people.users.add(self.profile.user_object)
        response = self.client.post(self.url, data={
            "bio_%d" % avail_bio.pk: ""}, follow=True)
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertTrue(
            updated_profile.bio_set.filter(pk=avail_bio.pk).exists())
        self.assertContains(response, "Sucessfully deleted profile %s." % (
            self.avail_profile.get_badge_name()))
        self.assertTrue(Act.objects.filter(bio__pk=avail_bio.pk,
                                           pk=context.acts[0].pk).exists())
        self.assertTrue(PeopleAllocation.objects.filter(
            event=context.sched_event,
            people__class_id=avail_bio.pk,
            people__commitment_class_id=context.acts[0].pk,
            people__users=self.profile.user_object).exists())
        self.assertFalse(PeopleAllocation.objects.filter(
            event=context.sched_event,
            people__class_id=avail_bio.pk,
            people__commitment_class_id=context.acts[0].pk,
            people__users=self.avail_profile.user_object).exists())
        self.assertNotContains(response,
                               "Skipped deletion because of errors above.")

    def test_move_booked_teacher_by_bid_submit(self):
        login_as(self.privileged_user, self)
        target_bio = BioFactory(contact=self.profile)
        avail_bio = BioFactory(contact=self.avail_profile)
        context = ClassContext(teacher=avail_bio)
        response = self.client.post(self.url, data={
            "bio_%d" % avail_bio.pk: target_bio.pk}, follow=True)
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertFalse(Bio.objects.filter(pk=avail_bio.pk).exists())
        self.assertContains(response, "Sucessfully deleted profile %s." % (
            self.avail_profile.get_badge_name()))
        self.assertContains(
            response,
            "Sucessfully deleted bio %s for profile %s." % (
                avail_bio.name,
                self.avail_profile.get_badge_name()))
        self.assertTrue(
            Class.objects.filter(teacher_bio__pk=target_bio.pk,
                                 pk=context.bid.pk).exists)
        self.assertTrue(PeopleAllocation.objects.filter(
            event=context.sched_event,
            people__class_id=target_bio.pk,
            people__users=self.profile.user_object).exists())

    def test_move_business_submit(self):
        login_as(self.privileged_user, self)
        vendor = VendorFactory()
        avail_vendor = VendorFactory()
        vendor.business.owners.add(self.profile)
        avail_vendor.business.owners.add(self.avail_profile)
        response = self.client.post(self.url, data={
            "business_%d" % avail_vendor.business.pk: ""}, follow=True)
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertTrue(
            updated_profile.business_set.filter(
                pk=avail_vendor.business.pk).exists())
        self.assertContains(response, "Sucessfully deleted profile %s." % (
            self.avail_profile.get_badge_name()))

    def test_move_shared_business_bids_submit(self):
        login_as(self.privileged_user, self)
        vendor = VendorFactory()
        avail_vendor = VendorFactory()
        vendor.business.owners.add(self.profile)
        avail_vendor.business.owners.add(self.avail_profile)
        response = self.client.post(
            self.url,
            data={
                "business_%d" % avail_vendor.business.pk: vendor.business.pk},
            follow=True)
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertTrue(Business.objects.filter(
            pk=avail_vendor.business.pk).exists())
        self.assertContains(response, "Sucessfully deleted profile %s." % (
            self.avail_profile.get_badge_name()))
        self.assertEqual(
            Vendor.objects.filter(business__pk=vendor.business.pk).count(),
            2)

    def test_move_solo_business_bids_submit(self):
        login_as(self.privileged_user, self)
        vendor = VendorFactory()
        avail_vendor = VendorFactory()
        vendor.business.owners.add(self.profile)
        for owner in avail_vendor.business.owners.all():
            avail_vendor.business.owners.remove(owner)
        avail_vendor.business.owners.add(self.avail_profile)

        response = self.client.post(
            self.url,
            data={
                "business_%d" % avail_vendor.business.pk: vendor.business.pk},
            follow=True)
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertFalse(Business.objects.filter(
            pk=avail_vendor.business.pk).exists())
        self.assertContains(response, "Sucessfully deleted profile %s." % (
            self.avail_profile.get_badge_name()))
        self.assertContains(
            response,
            "Sucessfully deleted business %s for profile %s." % (
                avail_vendor.business.name,
                self.avail_profile.get_badge_name()))
        self.assertEqual(
            Vendor.objects.filter(business__pk=vendor.business.pk).count(),
            2)

    def test_post_form_w_staff_lead(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        context = StaffAreaContext(staff_lead=self.avail_profile)
        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertContains(response, "Sucessfully deleted profile %s." % (
            self.avail_profile.get_badge_name()))
        self.assertTrue(StaffArea.objects.filter(
            pk=context.area.pk,
            staff_lead__pk=self.profile.pk).exists())

    def test_post_form_w_privs(self):
        # should exclude selected profile, and user's own profile
        login_as(self.privileged_user, self)
        grant_privilege(self.avail_profile, "Act Coordinator")
        grant_privilege(self.privileged_user, "Act Coordinator")
        grant_privilege(self.profile, "Class Coordinator")

        response = self.client.post(self.url, follow=True)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertContains(response, "Sucessfully deleted profile %s." % (
            self.avail_profile.get_badge_name()))
        # TODO - figure out why this doesn't work, or test with a future
        # version of django or pytest.  Can't explain why group gets deleted
        # w. user during testing
        # updated_user = User.objects.get(pk=self.profile.user_object.pk)
        # self.assertTrue(updated_user.groups.filter(
        #    name="Act Coordinator").exists())

    def test_move_evaluations(self):
        login_as(self.privileged_user, self)
        context = ClassContext()
        context.set_eval_answerer(self.profile)
        context.set_eval_answerer(self.avail_profile)

        response = self.client.post(self.url, data={}, follow=True)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertEqual(EventEvalGrade.objects.filter(
            user=self.profile.user_object).count(), 2)

    def test_move_bid_reviews(self):
        flex_evaluation = FlexibleEvaluationFactory(
            evaluator=self.avail_profile,
        )
        act_evaluation = ActBidEvaluationFactory(
            evaluator=self.avail_profile,
        )
        bid_evaluation = BidEvaluationFactory(
            evaluator=self.avail_profile,
        )
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={}, follow=True)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertTrue(ActBidEvaluation.objects.filter(
            pk=act_evaluation.pk,
            evaluator=self.profile).exists())
        self.assertTrue(BidEvaluation.objects.filter(
            pk=bid_evaluation.pk,
            evaluator=self.profile).exists())
        self.assertTrue(FlexibleEvaluation.objects.filter(
            pk=flex_evaluation.pk,
            evaluator=self.profile).exists())

    def test_move_article(self):
        article = ArticleFactory(creator=self.avail_profile)

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={}, follow=True)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertTrue(Article.objects.filter(
            pk=article.pk,
            creator=self.profile).exists())

    def test_move_purchaser(self):
        purchaser_target = PurchaserFactory(
            matched_to_user=self.profile.user_object)
        purchaser = PurchaserFactory(
            matched_to_user=self.avail_profile.user_object)

        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={}, follow=True)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertTrue(Purchaser.objects.filter(
            pk=purchaser.pk,
            matched_to_user=self.profile.user_object).exists())

    @patch('gbe.views.merge_profile_extra_view.get_schedule', autospec=True)
    def test_failed_to_reschedule(self, mocked_function):
        context = ShowContext()
        mocked_function.return_value = ScheduleResponse(
            schedule_items=[ScheduleItem(user=self.avail_profile.user_object,
                                         event=context.sched_event,
                                         booking_id=123)])
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={}, follow=True)
        self.assertRedirects(response,
                             reverse("manage_users", urlconf="gbe.urls"))
        self.assertContains(
            response,
            "Error - the merged profile is still booked for %s" % (
                context.sched_event.title + " - " +
                context.sched_event.starttime.strftime(GBE_DATETIME_FORMAT)))
        self.assertContains(
            response,
            "Skipped deletion because of errors above.  Contact the admin")
