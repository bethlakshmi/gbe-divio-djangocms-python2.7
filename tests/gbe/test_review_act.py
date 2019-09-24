from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
import nose.tools as nt
from django.test import TestCase
from django.test import Client
from tests.contexts import ActTechInfoContext
from tests.factories.gbe_factories import (
    ActCastingOptionFactory,
    ActFactory,
    ActBidEvaluationFactory,
    ConferenceFactory,
    EvaluationCategoryFactory,
    FlexibleEvaluationFactory,
    PersonaFactory,
    ProfileFactory,
    ShowFactory,
)
from tests.functions.gbe_functions import (
    clear_conferences,
    current_conference,
    grant_privilege,
    login_as,
    reload,
)
from tests.functions.scheduler_functions import assert_selected
from gbe.models import (
    ActBidEvaluation,
    FlexibleEvaluation,
)
from gbetext import (
    video_options,
    default_act_review_error_msg,
    default_act_review_success_msg,
)


class TestReviewAct(TestCase):
    '''Tests for review_act view'''

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Act Reviewers')
        grant_privilege(self.privileged_user, 'Act Coordinator')
        self.eval_cat = EvaluationCategoryFactory()
        self.eval_cat_invisible = EvaluationCategoryFactory(visible=False)
        self.act = ActFactory()
        self.url = reverse('act_review',
                           urlconf='gbe.urls',
                           args=[self.act.pk])

    def get_post_data(self,
                      bid,
                      show=None,
                      reviewer=None,
                      invalid=False):
        reviewer = reviewer or self.privileged_profile
        data = {str(self.eval_cat.pk) + '-ranking': 4,
                str(self.eval_cat.pk) + '-category': int(self.eval_cat.pk),
                str(self.eval_cat.pk) + '-evaluator': int(reviewer.pk),
                str(self.eval_cat.pk) + '-bid': int(bid.pk),
                'notes': "some notes",
                'evaluator': int(reviewer.pk),
                'bid': int(bid.pk),}
        if invalid:
            data[str(self.eval_cat.pk) + '-ranking'] = "cheese"
        return data

    def get_act_w_roles(self, act):
        ActCastingOptionFactory(casting="Regular Act",
                                show_as_special=False,
                                display_order=0)
        ActCastingOptionFactory(display_order=1)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        return self.client.get(url)

    def test_review_act_all_well(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)
        self.assertTrue('Review Information' in response.content)

    def test_hidden_fields_are_populated(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        evaluator_input = (
            '<input id="id_%d-evaluator" name="%d-evaluator" ' +
            'type="hidden" value="%d" />') % (
            self.eval_cat.pk,
            self.eval_cat.pk,
            self.privileged_profile.pk)
        bid_id_input = ('<input id="id_%d-bid" name="%d-bid" type="hidden" ' +
                        'value="%d" />') % (
            self.eval_cat.pk,
            self.eval_cat.pk,
            self.act.pk)
        self.assertContains(response, bid_id_input)
        self.assertContains(response, evaluator_input)

    def test_review_act_old_act(self):
        conference = ConferenceFactory(status="completed",
                                       accepting_bids=False)
        act = ActFactory(b_conference=conference)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('act_view', urlconf='gbe.urls', args=[act.pk]))
        self.assertTrue('Review Bids' in response.content)

    def test_review_act_non_privileged_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_review_act_post_first_time(self):
        clear_conferences()
        conference = ConferenceFactory(accepting_bids=True,
                                       status='upcoming')
        # conference = current_conference()
        act = ActFactory(accepted=1,
                         b_conference=conference)
        profile = ProfileFactory()
        user = profile.user_object
        grant_privilege(user, 'Act Reviewers')
        login_as(user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        data = self.get_post_data(act, profile)
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        expected_string = default_act_review_success_msg % (
            act.b_title, str(act.performer)
        )
        error_string = default_act_review_error_msg % (
            act.b_title)
        self.assertContains(response, expected_string)
        self.assertNotContains(response, error_string)

    def test_review_act_act_post_invalid_form(self):
        clear_conferences()
        conference = ConferenceFactory(accepting_bids=True,
                                       status='upcoming')
        act = ActFactory(accepted=1,
                         b_conference=conference)
        profile = ProfileFactory()
        user = profile.user_object
        grant_privilege(user, 'Act Reviewers')
        login_as(user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        data = self.get_post_data(act, invalid=True)
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        error_string = default_act_review_error_msg % (
            act.b_title)
        self.assertTrue(error_string in response.content)

    def test_review_act_load_existing_review(self):
        evaluation = FlexibleEvaluationFactory(
            evaluator=self.privileged_profile,
            category=self.eval_cat
        )
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[evaluation.bid.pk])
        login_as(self.privileged_user, self)

        response = self.client.get(url)
        chosen_item = ('<input checked="checked" id="id_%d-ranking_%d" ' +
                       'name="%d-ranking" type="radio" value="%d" />')
        test_result = chosen_item % (evaluation.category.pk,
                                     evaluation.ranking+1,
                                     evaluation.category.pk,
                                     evaluation.ranking)
        self.assertContains(response, test_result)
        self.assertContains(response, evaluation.category.category)
        self.assertContains(response, evaluation.category.help_text)

    def test_review_act_load_review_listing_test_avg(self):
        evaluation1 = FlexibleEvaluationFactory(
            evaluator=self.privileged_profile,
            category=self.eval_cat,
            ranking=0
        )
        evaluation2 = FlexibleEvaluationFactory(
            evaluator=ProfileFactory(),
            ranking=2,
            bid=evaluation1.bid
        )
        FlexibleEvaluationFactory(
            evaluator=evaluation2.evaluator,
            category=self.eval_cat,
            ranking=4,
            bid=evaluation1.bid
        )
        FlexibleEvaluationFactory(
            category=self.eval_cat,
            ranking=0,
            bid=evaluation1.bid
        )
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[evaluation1.bid.pk])
        login_as(self.privileged_user, self)

        response = self.client.get(url)
        reviewer_string = '<th class="rotate"><div><span>%s</span></div></th>'
        self.assertContains(response,
                            reviewer_string % str(evaluation1.evaluator))
        self.assertContains(response,
                            reviewer_string % str(evaluation2.evaluator))
        self.assertContains(response, evaluation1.category.category, 4)
        self.assertContains(response, evaluation2.category.category, 4)
        self.assertContains(response, "<td>2</td>", 1)
        self.assertContains(response, "<td>2.0</td>", 1)
        self.assertContains(response, "<td>1.33</td>", 1)
        self.assertContains(response, "<td>0</td>", 2)
        self.assertContains(response, "<td>4</td>", 1)

    def test_review_act_load_review_listing_invisible_categories(self):
        evaluation1 = FlexibleEvaluationFactory(
            evaluator=self.privileged_profile,
            category=self.eval_cat,
            ranking=0
        )
        evaluation2 = FlexibleEvaluationFactory(
            evaluator=self.privileged_profile,
            category=self.eval_cat_invisible,
            ranking=2,
            bid=evaluation1.bid
        )

        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[evaluation1.bid.pk])
        login_as(self.privileged_user, self)

        response = self.client.get(url)
        reviewer_string = '<th class="rotate"><div><span>%s</span></div></th>'
        self.assertContains(response,
                            reviewer_string % str(evaluation1.evaluator))
        self.assertContains(response, evaluation1.category.category, 4)
        self.assertNotContains(response, evaluation2.category.category)
        self.assertNotContains(response, "<td>2</td>")
        self.assertNotContains(response, "<td>2.0</td>")
        self.assertContains(response, "<td>0</td>", 1)
        self.assertContains(response, "<td>0.0</td>", 1)

    def test_review_act_load_review_all_blank_category(self):
        evaluation1 = FlexibleEvaluationFactory(
            evaluator=self.privileged_profile,
            category=self.eval_cat,
            ranking=-1
        )
        evaluation2 = FlexibleEvaluationFactory(
            evaluator=ProfileFactory(),
            category=self.eval_cat,
            ranking=-1,
            bid=evaluation1.bid
        )
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[evaluation1.bid.pk])
        login_as(self.privileged_user, self)

        response = self.client.get(url)
        self.assertContains(response, "<td></td>", 3)
        reviewer_string = '<th class="rotate"><div><span>%s</span></div></th>'
        self.assertContains(response,
                            reviewer_string % str(evaluation1.evaluator))
        self.assertContains(response,
                            reviewer_string % str(evaluation2.evaluator))
        self.assertContains(response, evaluation1.category.category, 4)

    def test_review_act_load_review_listing_new_cat(self):
        evaluation1 = FlexibleEvaluationFactory(
            evaluator=self.privileged_profile,
            category=self.eval_cat,
            ranking=0
        )
        evaluation2 = FlexibleEvaluationFactory(
            evaluator=ProfileFactory(),
            ranking=2,
            bid=evaluation1.bid
        )
        self.eval_cat_new = EvaluationCategoryFactory()

        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[evaluation1.bid.pk])
        login_as(self.privileged_user, self)

        response = self.client.get(url)
        reviewer_string = '<th class="rotate"><div><span>%s</span></div></th>'
        self.assertContains(response,
                            reviewer_string % str(evaluation1.evaluator))
        self.assertContains(response,
                            reviewer_string % str(evaluation2.evaluator))
        self.assertContains(response, evaluation1.category.category, 4)
        self.assertContains(response, evaluation2.category.category, 4)

    def test_review_act_update_review(self):
        eval = FlexibleEvaluationFactory(
            evaluator=self.privileged_profile,
            category=self.eval_cat
        )
        show = ShowFactory()
        login_as(self.privileged_user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[eval.bid.pk])
        data = self.get_post_data(
            eval.bid,
            reviewer=self.privileged_profile,
            show=show
            )
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        evals = FlexibleEvaluation.objects.filter(
            evaluator=self.privileged_profile,
            bid=eval.bid
        )
        self.assertTrue(len(evals), 1)
        self.assertTrue(evals[0].ranking, 4)
        expected_string = default_act_review_success_msg % (
            eval.bid.b_title, str(eval.bid.performer)
        )
        self.assertContains(response, expected_string)

    def test_review_act_update_notes(self):
        notes = ActBidEvaluationFactory()
        show = ShowFactory()
        login_as(self.privileged_user, self)
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[notes.bid.pk])
        data = self.get_post_data(
            notes.bid,
            reviewer=self.privileged_profile,
            show=show
            )
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        new_notes = ActBidEvaluation.objects.filter(
            evaluator=self.privileged_profile,
            bid=notes.bid
        )
        self.assertTrue(len(new_notes), 1)
        self.assertTrue(new_notes[0].notes, "some notes")
        expected_string = default_act_review_success_msg % (
            notes.bid.b_title, str(notes.bid.performer)
        )
        self.assertContains(response, expected_string)

    def test_review_act_no_review(self):
        login_as(self.privileged_user, self)
        data = self.get_post_data(self.act, self.privileged_user)
        del data[str(self.eval_cat.pk) + '-ranking']
        response = self.client.post(self.url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        evals = FlexibleEvaluation.objects.filter(
            evaluator=self.privileged_profile,
            bid=self.act,
            category=self.eval_cat
        )
        self.assertTrue(len(evals), 1)
        self.assertTrue(evals[0].ranking, -1)

    def test_video_choice_display(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        assert 'Video Notes:' in response.content
        assert video_options[1][1] not in response.content

    def test_review_summer_act(self):
        act = ActFactory(b_conference__act_style="summer")
        url = reverse('act_review',
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('The Summer Act' in response.content)

    def test_review_default_role_present(self):
        response = self.get_act_w_roles(self.act)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<option value="" selected="selected">Regular Act</option>')

    def test_review_special_role_present(self):
        response = self.get_act_w_roles(self.act)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<option value="Hosted by...">Hosted by...</option>')

    def test_review_special_role_already_cast(self):
        context = ActTechInfoContext(act_role="Hosted by...")
        response = self.get_act_w_roles(context.act)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<option value="Hosted by..." selected="selected"' +
            '>Hosted by...</option>')
