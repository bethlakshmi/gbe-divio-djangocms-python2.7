from django.urls import reverse
from django.contrib.auth.models import User
from django.test import (
    Client,
    TestCase,
)
from datetime import (
    datetime,
    timedelta,
)
from tests.contexts import (
    ClassContext,
)
from tests.factories.scheduler_factories import EventEvalQuestionFactory
from gbe.models import Conference
from scheduler.models import (
    EventEvalQuestion,
    EventEvalGrade,
    EventEvalComment,
    EventEvalBoolean,
    EventItem,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    login_as,
    make_admission_purchase,
)
from gbe_utils.text import no_profile_msg
from gbetext import (
    eval_as_presenter_error,
    eval_success_msg,
    full_login_msg,
    new_grade_options,
    no_login_msg,
    not_purchased_msg,
    not_ready_for_eval,
    one_eval_msg,
)


class TestEvalEventView(TestCase):
    view_name = 'eval_event'

    def setUp(self):
        self.client = Client()
        self.context = ClassContext(starttime=datetime.now()-timedelta(days=1))
        self.q0 = self.context.setup_eval()
        self.profile = ProfileFactory()
        make_admission_purchase(self.context.conference,
                                self.profile.user_object,
                                include_most=True,
                                include_conference=True)
        self.url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.sched_event.pk])

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('register',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Create an Account")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            full_login_msg % (no_login_msg, reverse(
                'login',
                urlconf='gbe.urls') + "?next=" + self.url))

    def test_get_unfinished_user(self):
        unfinished = UserFactory()
        login_as(unfinished, self)
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('register',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Create an Account")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            no_profile_msg)

    def test_post_unfinished_user(self):
        unfinished = UserFactory()
        login_as(unfinished, self)
        response = self.client.post(self.url, follow=True)
        redirect_url = reverse('register',
                               urlconf='gbe.urls') + "?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertContains(response, "Create an Account")
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            no_profile_msg)

    def test_get_eval(self):
        q1 = EventEvalQuestionFactory(answer_type="grade")
        q2 = EventEvalQuestionFactory(answer_type="text",
                                      help_text="so helpful")
        q3 = EventEvalQuestionFactory(answer_type="boolean")
        q4 = EventEvalQuestionFactory(visible=False,
                                      help_text="unhelpful")
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        self.assertContains(response, self.context.bid.e_title)
        self.assertContains(response, self.context.teacher)
        self.assertContains(response, q1.question)
        self.assertContains(response, q2.question)
        self.assertContains(response, q2.help_text)
        self.assertContains(response, q3.question)
        self.assertNotContains(response, q4.question)
        self.assertNotContains(response, q4.help_text)
        n = 0

        grade_input = '<input type="radio" name="question%d" value="%s" ' + \
                      'required id="id_question%d_%d" %s/>'
        answer_textarea = '<textarea name="question%d" cols="40" ' + \
            'rows="10" id="id_question%d">'

        boolean_checkbox = '<input type="checkbox" name="question%d" ' + \
            'id="id_question%d" />'
        for grade in new_grade_options:
            g = grade[0]
            checked = ""
            if grade[0] is None:
                g = ""
                checked = "checked "
            self.assertContains(
                response,
                grade_input % (q1.pk, g, q1.pk, n, checked),
                html=True)
            n = n + 1
        self.assertContains(
            response,
            answer_textarea % (q2.pk, q2.pk),
            html=True)
        self.assertContains(
            response,
            boolean_checkbox % (q3.pk, q3.pk),
            html=True)

    def test_get_eval_own_class(self):
        q1 = EventEvalQuestionFactory(answer_type="grade")
        q2 = EventEvalQuestionFactory(answer_type="text",
                                      help_text="so helpful")
        q3 = EventEvalQuestionFactory(answer_type="boolean")
        q4 = EventEvalQuestionFactory(visible=False,
                                      help_text="unhelpful")
        login_as(self.context.teacher.contact, self)
        response = self.client.get(self.url, follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            eval_as_presenter_error)

    def test_get_no_purchase(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url, follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            not_purchased_msg)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))

    def test_post_no_purchase(self):
        login_as(ProfileFactory(), self)
        response = self.client.post(self.url, follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            not_purchased_msg)

    def test_bad_occurrence_id(self):
        login_as(self.profile, self)
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.sched_event.pk + 1000])
        response = self.client.get(url, follow=True)
        assert_alert_exists(
            response,
            'danger',
            'Error',
            "An error has occurred.  Occurrence id %d not found" % (
                self.context.sched_event.pk + 1000))

    def test_get_future_class(self):
        login_as(self.profile, self)
        future_context = ClassContext(
            starttime=datetime.now()+timedelta(days=1),
            conference=self.context.conference)
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[future_context.sched_event.pk])
        response = self.client.get(url, follow=True)
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            "The event hasn't occurred yet, and can't be rated.")

    def test_post_future_class(self):
        login_as(self.profile, self)
        future_context = ClassContext(
            starttime=datetime.now()+timedelta(days=1),
            conference=self.context.conference)
        url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[future_context.sched_event.pk])
        response = self.client.post(url,
                                    data={'question%d' % self.q0.pk: "C", },
                                    follow=True)
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            "The event hasn't occurred yet, and can't be rated.")

    def test_no_questions(self):
        EventEvalQuestion.objects.all().delete()
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            not_ready_for_eval)

    def test_already_answered(self):
        self.context.set_eval_answerer(self.profile)
        login_as(self.profile, self)
        response = self.client.get(self.url, follow=True)
        assert_alert_exists(
            response,
            'warning',
            'Warning',
            one_eval_msg)

    def test_invalid_eval(self):
        login_as(self.profile, self)
        response = self.client.post(
            self.url,
            data={'question%d' % self.q0.pk: "invalid", },
            follow=True)
        self.assertContains(
            response,
            'Select a valid choice. invalid is not one of the available ' +
            'choices.')

    def test_set_eval(self):
        login_as(self.profile, self)
        redirect = reverse(
            "detail_view",
            urlconf="gbe.scheduling.urls",
            args=[self.context.bid.eventitem_id])
        response = self.client.post(
            "%s?next=%s" % (self.url, redirect),
            data={'question%d' % self.q0.pk: 2, },
            follow=True)
        assert_alert_exists(
            response,
            'info',
            'Info',
            eval_success_msg)
        self.assertRedirects(response, redirect)
