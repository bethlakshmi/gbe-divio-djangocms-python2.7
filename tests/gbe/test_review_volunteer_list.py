from django.urls import reverse
from django.test import TestCase
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
    VolunteerEvaluationFactory,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from gbetext import role_commit_map


class TestReviewVolunteerlist(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfileFactory()
        grant_privilege(cls.profile, 'Act Coordinator')
        cls.url = reverse('volunteer_review', urlconf="gbe.urls")
        cls.context = VolunteerContext()

    def test_review_not_visible_without_permission(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_volunteer_not_yet_reviewed(self):
        '''staff_area view should load
        '''
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, self.context.opp_event.title)
        self.assertContains(response, self.context.sched_event.title)
        self.assertContains(response, reverse(
            'mail_to_individual',
            urlconf='gbe.email.urls',
            args=[self.context.profile.pk]))
        self.assertContains(response, reverse(
            'volunteer-review-add',
            urlconf='gbe.urls',
            args=[self.context.conference.conference_slug,
                  self.context.profile.pk]))
        self.assertContains(response, self.context.profile.get_badge_name())
        self.assertContains(response, self.context.profile.phone)
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-info">')

    def test_show_with_inactive(self):
        ''' view should load
        '''
        inactive = ProfileFactory(
            display_name="Inactive User",
            user_object__is_active=False
        )
        context = VolunteerContext(profile=inactive,
                                   conference=self.context.conference)
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, context.sched_event.title)
        self.assertContains(response, context.opp_event.title)
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-danger">')
        self.assertContains(response, inactive.display_name)

    def test_other_conference_review_completed(self):
        '''staff_area view should load everything but rejected
            same code for event & staff area, so not retesting
        '''
        context = StaffAreaContext()
        context.conference.status = "completed"
        context.conference.save()
        vol1, opp1 = context.book_volunteer()
        opp2 = context.add_volunteer_opp()
        vo2, book2 = context.book_volunteer(volunteer_sched_event=opp2,
                                            volunteer=vol1)
        review = VolunteerEvaluationFactory(
            evaluator=self.profile,
            volunteer=vol1,
            conference=context.conference)
        login_as(self.profile, self)
        response = self.client.get("%s?conf_slug=%s" % (
            self.url,
            context.conference.conference_slug))
        self.assertContains(response, str(vol1))
        self.assertContains(response, opp1.event.title)
        self.assertContains(response, opp2.title)
        self.assertContains(response, reverse(
            'volunteer-review-update',
            urlconf='gbe.urls',
            args=[review.pk]))
        self.assertNotContains(response, reverse(
            'volunteer-review-add',
            urlconf='gbe.urls',
            args=[context.conference.conference_slug, vol1.pk]))
        self.assertContains(
            response,
            "<b>Reviewer:</b> %s" % self.profile.display_name)
        self.assertContains(
            response,
            "<b>Comment:</b> %s" % review.notes)

    def test_volunteer_review_changed(self):
        '''staff_area view should load
        '''
        login_as(self.profile, self)
        review = VolunteerEvaluationFactory(
            evaluator=self.profile,
            volunteer=self.context.profile,
            conference=self.context.conference)
        response = self.client.get(
            "%s?changed_id=%s" % (self.url, review.volunteer.pk))
        self.assertContains(response, self.context.opp_event.title)
        self.assertContains(
            response,
            '<tr class="gbe-table-row gbe-table-success">')
