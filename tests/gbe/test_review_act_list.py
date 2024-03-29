from django.test import TestCase
from django.urls import reverse
from django.test import Client
from tests.factories.gbe_factories import (
    ActBidEvaluationFactory,
    ActCastingOptionFactory,
    ActFactory,
    BioFactory,
    ConferenceFactory,
    FlexibleEvaluationFactory,
    ProfileFactory,
    UserFactory,
)
from tests.contexts import ShowContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbe.models import EvaluationCategory
from gbetext import (
    act_shows_options_short,
    apply_filter_msg,
    clear_filter_msg,
    no_filter_msg,
)


class TestReviewActList(TestCase):
    '''Tests for review_act_list view'''
    view_name = 'act_review'
    metric_row = '<tr class="gbe-table-row"><td>%s</td><td>%d</td></tr>'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse(
            cls.view_name,
            urlconf='gbe.urls')
        cls.performer = BioFactory()
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Act Reviewers')
        cls.conference = ConferenceFactory(status='upcoming')
        cls.acts = ActFactory.create_batch(
            4,
            b_conference=cls.conference,
            submitted=True,
            shows_preferences=['8', '9'])

    def setUp(self):
        self.client = Client()

    def test_review_act_list_all_well(self):
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Act Proposals')
        for choice in act_shows_options_short:
            self.assertContains(response, choice[1])

    def test_review_act_list_inactive_user(self):
        inactive = ActFactory(
            submitted=True,
            b_conference=self.conference,
            bio__contact__user_object__is_active=False)
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertContains(response, 'gbe-table-row gbe-table-danger')

    def test_review_act_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_review_act_no_profile(self):
        login_as(UserFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_review_act_assigned_show(self):
        context = ShowContext()
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': context.conference.conference_slug})
        self.assertContains(response, context.acts[0].b_title)
        self.assertContains(response, context.sched_event.title)
        self.assertContains(response, self.metric_row % ("Accepted", 1))

    def test_review_act_assigned_show_role(self):
        context = ShowContext(act_role="Hosted By...")
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': context.conference.conference_slug})
        self.assertContains(response, context.sched_event.title)
        self.assertContains(response, "Hosted By...")
        self.assertContains(response, self.metric_row % ("Accepted", 1))

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
        self.assertContains(response, context.sched_event.title)
        self.assertContains(response, context2.sched_event.title)
        self.assertContains(response, self.metric_row % ("Accepted", 1))

    def test_review_act_has_reviews(self):
        ActBidEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile)
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
        self.assertContains(response, 'gbe-table-row gbe-table-success')
        self.assertContains(response, self.metric_row % ("No Decision", 4))
        self.assertContains(response, self.metric_row % (
            self.privileged_profile.display_name,
            1), html=True)

    def test_review_act_has_empty_reviews(self):
        ActBidEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile)
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
        self.assertContains(response, 'gbe-table-row gbe-table-info')
        self.assertContains(response, self.metric_row % ("No Decision", 4))
        self.assertContains(response, self.metric_row % (
            "Acts with no review at all",
            3), html=True)
        self.assertContains(
            response,
            ('<tr class="gbe-table-row"><td><b>Total Acts Pending Review' +
             '</b></td><td><b>4</b></td></tr>'),
            html=True)

    def test_review_act_has_average(self):
        ActBidEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile)
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
        self.assertContains(response, '<td>--</td>', 12)
        self.assertContains(response, self.metric_row % (
            self.privileged_profile.display_name,
            1), html=True)
        # 2 because there's 1 review in metrics, and 1 review on the bid row
        self.assertContains(response, "<td>1</td>", 2)
        self.assertContains(response, "<td>0</td>", 3)

    def test_review_act_has_average_w_zero(self):
        EvaluationCategory.objects.all().delete()
        ActBidEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile)
        flex_eval = FlexibleEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile,
            )
        flex_eval = FlexibleEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile,
            ranking=0)
        flex_eval = FlexibleEvaluationFactory(
            bid=self.acts[0],
            evaluator=self.privileged_profile,
            ranking=5)
        login_as(self.privileged_user, self)
        response = self.client.get(
            self.url,
            data={'conf_slug': self.conference.conference_slug})
        self.assertContains(response, "0.0", 1)
        self.assertContains(response, "5.0", 1)
        self.assertContains(response, "3.0", 1)
        self.assertContains(response, "2.67", 1)
        self.assertContains(response, self.metric_row % (
            self.privileged_profile.display_name,
            1), html=True)

    def test_review_act_list_filter(self):
        other_show = ActFactory(
            b_conference=self.conference,
            submitted=True,
            shows_preferences=['10'])
        no_pref_show = ActFactory(
            b_conference=self.conference,
            submitted=True,
            shows_preferences=[])
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={'shows_preferences': ['9'],
                  'filter': "Filter Interest"})
        self.assertContains(response, apply_filter_msg)
        self.assertContains(response, self.acts[0].b_title)
        self.assertNotContains(response, other_show.b_title)
        self.assertNotContains(response, no_pref_show.b_title)

    def test_review_act_list_clear_filter(self):
        other_show = ActFactory(
            b_conference=self.conference,
            submitted=True,
            shows_preferences=['9'])
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={'shows_preferences': [],
                  'filter': "Filter Interest"})
        self.assertContains(response, clear_filter_msg)
        self.assertContains(response, self.acts[0].b_title)
        self.assertContains(response, other_show.b_title)

    def test_review_act_list_bad_filter(self):
        other_show = ActFactory(
            b_conference=self.conference,
            submitted=True,
            shows_preferences=['9'])
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data={'shows_preferences': ['27'],
                  'filter': "Filter Interest"})
        self.assertContains(response, no_filter_msg)
        self.assertContains(response, self.acts[0].b_title)
        self.assertContains(response, other_show.b_title)
