from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    BioFactory,
    ClassFactory,
    ClassLabelFactory,
    ConferenceFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import SchedEventFactory
from tests.functions.gbe_functions import (
    assert_option_state,
    grant_privilege,
    is_login_page,
    login_as,
)
from gbe.models import BidEvaluation
from scheduler.models import Event as sEvent
from gbe_forms_text import difficulty_default_text


class TestReviewClass(TestCase):
    '''Tests for review_class view'''
    view_name = 'class_review'

    @classmethod
    def setUpTestData(cls):
        cls.performer = BioFactory()
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Class Reviewers')
        grant_privilege(cls.privileged_user, 'Class Coordinator')

    def setUp(self):
        self.client = Client()

    def get_post_data(self, bid, reviewer=None):
        reviewer = reviewer or self.privileged_profile
        return {'vote': 3,
                'notes': "blah blah",
                'evaluator': reviewer.pk,
                'bid': bid.pk}

    def test_review_class_all_well(self):
        klass = ClassFactory(difficulty="Hard")
        orig_label = ClassLabelFactory()
        klass.labels.add(orig_label)
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Review Class')
        self.assertContains(response, "Class Proposal")
        self.assertContains(response, "Set Class State")
        self.assertNotContains(response, 'name="extra_button"')
        self.assertContains(response, self.performer.year_started)
        self.assertContains(response, difficulty_default_text["Hard"])
        assert_option_state(response, orig_label.pk, orig_label.text, True)

    def test_review_class_w_scheduling(self):
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertContains(response, 'name="extra_button"')

    def test_review_class_post_form_invalid(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data={'accepted': 1})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Review Class')

    def test_review_class_post_form_valid_creates_evaluation(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        profile = self.privileged_user.profile
        pre_execute_count = BidEvaluation.objects.filter(
            evaluator=profile,
            bid=klass).count()
        login_as(self.privileged_user, self)
        data = self.get_post_data(klass)
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Review Class')
        post_execute_count = BidEvaluation.objects.filter(
            evaluator=profile,
            bid=klass).count()
        assert post_execute_count == pre_execute_count + 1

    def test_review_class_valid_post_evaluation_has_correct_vote(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')
        profile = self.privileged_user.profile
        login_as(self.privileged_user, self)
        data = self.get_post_data(klass)
        response = self.client.post(url,
                                    data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Review Class')
        evaluation = BidEvaluation.objects.filter(
            evaluator=profile,
            bid=klass).last()
        assert evaluation.vote == data['vote']

    def test_review_class_past_conference(self):
        klass = ClassFactory()
        klass.b_conference.status = 'completed'
        klass.b_conference.save()
        url = reverse(self.view_name, args=[klass.pk], urlconf="gbe.urls")
        login_as(self.privileged_user, self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse('class_view',
                    urlconf='gbe.urls',
                    args=[klass.pk]))
        self.assertContains(response, 'Review Class')
        self.assertNotContains(response, 'Review Information')

    def test_no_login_gives_error(self):
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login') + "?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_basic_user(self):
        klass = ClassFactory()
        reviewer = ProfileFactory()
        grant_privilege(reviewer, 'Class Reviewers')
        login_as(reviewer, self)
        url = reverse(self.view_name, args=[klass.pk], urlconf="gbe.urls")
        response = self.client.get(url)
        self.assertContains(response, "Class Proposal")
        assert response.status_code == 200

    def test_review_class_no_how_heard(self):
        klass = ClassFactory()
        klass.teacher_bio.contact.how_heard = '[]'
        klass.teacher_bio.contact.save()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertNotContains(response, '[]')
        self.assertContains(response, "The Presenter")

    def test_review_class_how_heard_is_present(self):
        klass = ClassFactory()
        klass.teacher_bio.contact.how_heard = "[u'Facebook']"
        klass.teacher_bio.contact.save()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertContains(response, 'Facebook')
