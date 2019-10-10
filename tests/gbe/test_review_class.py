from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
    ConferenceFactory,
    PersonaFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import SchedEventFactory
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from gbe.models import BidEvaluation
from scheduler.models import Event as sEvent


class TestReviewClass(TestCase):
    '''Tests for review_class view'''
    view_name = 'class_review'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.performer = PersonaFactory()
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Class Reviewers')
        grant_privilege(self.privileged_user, 'Class Coordinator')

    def get_post_data(self, bid, reviewer=None):
        reviewer = reviewer or self.privileged_profile
        return {'vote': 3,
                'notes': "blah blah",
                'evaluator': reviewer.pk,
                'bid': bid.pk}

    def test_review_class_all_well(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

    def test_review_class_post_form_invalid(self):
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.post(url,
                                    data={'accepted': 1})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Bid Information' in response.content)

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
        self.assertTrue('Bid Information' in response.content)
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
        self.assertTrue('Bid Information' in response.content)
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
        self.assertTrue('Bid Information' in response.content)
        self.assertFalse('Review Information' in response.content)

    def test_no_login_gives_error(self):
        url = reverse(self.view_name, args=[1], urlconf="gbe.urls")
        response = self.client.get(url, follow=True)
        redirect_url = reverse('login', urlconf='gbe.urls') + "/?next=" + url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_basic_user(self):
        klass = ClassFactory()
        reviewer = ProfileFactory()
        grant_privilege(reviewer, 'Class Reviewers')
        login_as(reviewer, self)
        url = reverse(self.view_name, args=[klass.pk], urlconf="gbe.urls")
        response = self.client.get(url)
        assert "Review Bids" in response.content
        assert response.status_code == 200

    def test_review_class_no_how_heard(self):
        klass = ClassFactory()
        klass.teacher.contact.how_heard = '[]'
        klass.teacher.contact.save()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        assert '[]' not in response.content
        assert "The Presenter" in response.content

    def test_review_class_how_heard_is_present(self):
        klass = ClassFactory()
        klass.teacher.contact.how_heard = "[u'Facebook']"
        klass.teacher.contact.save()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(self.privileged_user, self)
        response = self.client.get(url)
        assert 'Facebook' in response.content
