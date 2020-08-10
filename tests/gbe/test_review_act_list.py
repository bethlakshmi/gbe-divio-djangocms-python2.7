import nose.tools as nt
from django.test import TestCase
from django.urls import reverse
from django.test.client import RequestFactory
from django.test import Client
from tests.factories.gbe_factories import (
    ActCastingOptionFactory,
    ActFactory,
    ConferenceFactory,
    FlexibleEvaluationFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.contexts import ShowContext
from tests.functions.gbe_functions import (
    current_conference,
    grant_privilege,
    login_as,
)
from django.core.exceptions import PermissionDenied


class TestReviewActList(TestCase):
    '''Tests for review_act_list view'''
    view_name = 'act_review'

    def setUp(self):
        self.url = reverse(
            self.view_name,
            urlconf='gbe.urls')
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Act Reviewers')
        self.conference = current_conference()
        self.acts = ActFactory.create_batch(
            4,
            b_conference=self.conference,
            submitted=True)

    def test_review_act_list_all_well(self):
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        nt.assert_equal(response.status_code, 200)
        self.assertContains(response, 'Bid Information')

    def test_review_act_list_inactive_user(self):
        inactive = ActFactory(
            submitted=True,
            b_conference=self.conference,
            performer__contact__user_object__is_active=False)
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertContains(response, 'bid-table danger')

    def test_review_act_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        nt.assert_equal(403, response.status_code)

    def test_review_act_no_profile(self):
        login_as(UserFactory(), self)
        response = self.client.get(self.url)
        nt.assert_equal(403, response.status_code)

    def test_review_act_assigned_show(self):
        context = ShowContext()
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': context.conference.conference_slug})
        self.assertContains(response, context.acts[0].b_title)
        self.assertContains(response, context.show.e_title)

    def test_review_act_assigned_show_role(self):
        context = ShowContext(act_role="Hosted By...")
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': context.conference.conference_slug})
        self.assertContains(response, context.show.e_title)
        self.assertContains(response, "Hosted By...")

    def test_review_act_assigned_two_shows(self):
        context = ShowContext()
        context2 = ShowContext(
            conference=context.conference,
            act=context.acts[0])
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': context.conference.conference_slug})
        self.assertContains(response, context.acts[0].b_title)
        self.assertContains(response, "%s - Performing" % context.show.e_title)
        self.assertContains(response, "%s - Performing" % (
            context2.show.e_title))

    def test_review_act_has_reviews(self):
        flex_eval = FlexibleEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile,
            )
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug,
                  'changed_id': self.acts[0].id})
        self.assertContains(response, str(flex_eval.category.category))
        self.assertContains(response, str(flex_eval.ranking))
        self.assertContains(response, "No Decision")
        self.assertContains(response, 'bid-table success')

    def test_review_act_has_empty_reviews(self):
        flex_eval = FlexibleEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile,
            ranking=-1,
            )
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertContains(response, str(flex_eval.category.category))
        self.assertContains(response, str("--"))
        self.assertContains(response, "Needs Review")
        self.assertContains(response, 'bid-table info')

    def test_review_act_has_average(self):
        flex_eval = FlexibleEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile,
            )
        flex_eval = FlexibleEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile,
            ranking=4)
        flex_eval = FlexibleEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile,
            ranking=4)
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertContains(response, str(3.67))
        self.assertContains(response, str(flex_eval.ranking))
        self.assertContains(response, "4.0", 2)
        self.assertContains(response, '<td class="bid-table">--</td>', 12)
