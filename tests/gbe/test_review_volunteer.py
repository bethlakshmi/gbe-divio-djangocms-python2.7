from django.test import TestCase
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone
from tests.factories.gbe_factories import (
    ConferenceFactory,
    VolunteerEvaluationFactory,
    UserMessageFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
)
from gbetext import (
    update_vol_eval_msg,
)
from gbe.models import (
    VolunteerEvaluation,
    UserMessage,
)


formset_data = {
    'vote': 3,
    'notes': "flat text about volunteer's efforts",
}


class TestVolunteerEvalCreate(TestCase):
    view_name = 'volunteer-review-add'

    def setUp(self):
        UserMessage.objects.all().delete()

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Act Coordinator')
        cls.volunteer = ProfileFactory()
        cls.conference = ConferenceFactory()
        cls.url = reverse(
            cls.view_name,
            urlconf='gbe.urls',
            args=[cls.conference.conference_slug,
                  cls.volunteer.pk])

    def test_get(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            '<a href="#" data-toggle="modal" data-target="#DeleteModal" ' +
            'data-backdrop="true" class="btn gbe-btn-secondary">Delete</a>',
            html=True)
        self.assertContains(
            response,
            '<textarea name="notes" cols="40" rows="10" id="id_notes">' +
            '</textarea>',
            html=True)

    def test_submit(self):
        ''' making a custom success message '''
        msg = UserMessageFactory(
            view='VolunteerEvalCreate',
            code='SUCCESS')
        login_as(self.privileged_user, self)
        reviews = VolunteerEvaluation.objects.all().count()
        response = self.client.post(
            self.url,
            formset_data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            1,
            VolunteerEvaluation.objects.all().count()-reviews)
        latest = VolunteerEvaluation.objects.order_by('pk').last()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
        self.assertRedirects(response, "%s?changed_id=%d" % (
            reverse('volunteer_review', urlconf='gbe.urls'),
            latest.pk))
        self.assertEqual(latest.conference.pk, self.conference.pk)
        self.assertEqual(latest.volunteer.pk, self.volunteer.pk)

    def test_submit_invalid(self):
        # no pronoun values supplied in either field
        login_as(self.privileged_user, self)
        count = VolunteerEvaluation.objects.all().count()
        response = self.client.post(self.url, {'notes': 'no vote'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.", 1)
        self.assertEqual(count, VolunteerEvaluation.objects.all().count())


class TestVolunteerEvalUpdate(TestCase):
    view_name = 'volunteer-review-update'

    def setUp(self):
        UserMessage.objects.all().delete()

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Act Coordinator')
        cls.review = VolunteerEvaluationFactory()
        grant_privilege(cls.review.evaluator, 'Act Coordinator')
        cls.url = reverse(cls.view_name,
                          urlconf='gbe.urls',
                          args=[cls.review.pk])

    def test_get(self):
        login_as(self.review.evaluator, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<a href="#" data-toggle="modal" data-target="#DeleteModal" ' +
            'data-backdrop="true" class="btn gbe-btn-secondary">Delete</a>',
            html=True)
        self.assertContains(
            response,
            reverse("volunteer-review-delete",
                    urlconf="gbe.urls",
                    args=[self.review.pk]))
        self.assertContains(
            response,
            ('<textarea name="notes" cols="40" rows="10" id="id_notes">%s' +
            '</textarea>') % self.review.notes,
            html=True)

    def test_get_wrong_review(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(404, response.status_code)

    def test_submit(self):
        login_as(self.review.evaluator, self)
        response = self.client.post(
            self.url,
            formset_data,
            follow=True
        )
        review_reloaded = VolunteerEvaluation.objects.get(pk=self.review.pk)
        self.assertEqual(review_reloaded.notes, formset_data['notes'])
        self.assertRedirects(response, "%s?changed_id=%d" % (
            reverse('volunteer_review', urlconf='gbe.urls'),
            review_reloaded.pk))
        assert_alert_exists(
            response, 'success', 'Success', update_vol_eval_msg)


class TestVolunteerEvalDelete(TestCase):
    view_name = 'volunteer-review-delete'

    def setUp(self):
        self.review = VolunteerEvaluationFactory()
        grant_privilege(self.review.evaluator, 'Act Coordinator')
        self.url = reverse(self.view_name,
                           urlconf="gbe.urls",
                           args=[self.review.pk])

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Act Coordinator')

    def test_delete(self):
        login_as(self.review.evaluator, self)
        response = self.client.post(self.url,
                                    data={'submit': 'Confirm'},
                                    follow=True)
        self.assertRedirects(response,
                             reverse('volunteer_review', urlconf="gbe.urls"))
        assert_alert_exists(
            response,
            'success',
            'Success',
            "Successfully deleted review for '%s'" % str(
                self.review.volunteer.get_badge_name()))

    def test_delete_wrong_review(self):
        login_as(self.privileged_user, self)
        response = self.client.post(self.url,
                                    data={'submit': 'Confirm'},
                                    follow=True)
        self.assertEqual(404, response.status_code)
