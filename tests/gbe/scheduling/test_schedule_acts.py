from django.urls import reverse
from django.test import (
    Client,
    TestCase
)
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
    ShowFactory
)
from tests.factories.scheduler_factories import (
    ResourceAllocationFactory,
    OrderingFactory,
    WorkerFactory
)
from scheduler.models import (
    EventItem,
    ResourceAllocation
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as
)
from tests.contexts import ShowContext


class TestScheduleActs(TestCase):
    view_name = 'schedule_acts'

    def setUp(self):
        self.client = Client()
        self.user = ProfileFactory.create().user_object
        self.privileged_profile = ProfileFactory()
        self.privileged_user = self.privileged_profile.user_object
        grant_privilege(self.privileged_user, 'Scheduling Mavens')
        self.context = ShowContext()
        self.url = reverse(self.view_name,
                           urlconf="gbe.scheduling.urls",
                           args=[self.context.show.pk])

    def get_basic_post(self):
        allocation = self.context.sched_event.resources_allocated.filter(
            ordering__class_id=self.context.acts[0].pk).first()
        data = {
            '%d-performer' %
            self.context.acts[0].pk: 'changed performer',
            '%d-title' %
            self.context.acts[0].pk: 'changed title',
            '%d-booking_id' %
            self.context.acts[0].pk: allocation.pk,
            '%d-show' %
            self.context.acts[0].pk: str(
                self.context.sched_event.pk),
            '%d-order' % self.context.acts[0].pk: 1}
        return data

    def assert_good_form_display(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'<ul class="errorlist">', response.content)
        for act in self.context.acts:
            self.assertContains(response, act.b_title)
            self.assertContains(response, str(act.performer))
        self.assertContains(
            response,
            '<option value="%d" selected>%s</option>' % (
                self.context.sched_event.pk,
                self.context.show.e_title)
            )

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse(
            'login',
            urlconf='gbe.urls') + "/?next=" + self.url
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_bad_show(self):
        login_as(self.privileged_profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[self.context.show.pk+1])
        response = self.client.get(bad_url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_good_user_get_unscheduled_show(self):
        show = ShowFactory()
        login_as(self.privileged_profile, self)
        show_request_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls",
            args=[show.pk])
        response = self.client.get(show_request_url, follow=True)
        self.assertContains(response,
                            "Schedule for show id %d not found" % show.pk)

    def test_good_user_get_no_show(self):
        login_as(self.privileged_profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls")
        response = self.client.get(bad_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Select a current or upcoming show to schedule")
        self.assertContains(
            response,
            '<option value="%s">%s</option>' % (
                self.context.show.pk,
                self.context.show.e_title)
            )

    def test_post_no_show(self):
        login_as(self.privileged_profile, self)
        bad_url = reverse(
            self.view_name,
            urlconf="gbe.scheduling.urls")
        response = self.client.post(bad_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            "Select a current or upcoming show to schedule")
        self.assertContains(
            response,
            '<option value="%s">%s</option>' % (
                self.context.show.pk,
                self.context.show.e_title)
            )

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assert_good_form_display(response)

    def test_good_user_get_no_acts(self):
        no_act_context = ShowContext(act=ActFactory(
            accepted=2,
            b_conference=self.context.conference))
        no_act_url = reverse(self.view_name,
                             urlconf="gbe.scheduling.urls",
                             args=[no_act_context.show.pk])
        login_as(self.privileged_profile, self)
        response = self.client.get(no_act_url)
        self.assertContains(response, "No Acts have been cast in this show")

    def test_good_user_get_inactive_user(self):
        inactive = ProfileFactory(
            display_name="Inactive Profile",
            user_object__is_active=False
        )
        inactive_act = ActFactory(performer__contact=inactive,
                                  accepted=3,
                                  submitted=True)
        self.context.book_act(act=inactive_act)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertIn(b'bgcolor="red"', response.content)

    def test_good_user_get_two_shows_same_title(self):
        ShowFactory(e_title=self.context.show.e_title)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assert_good_form_display(response)

    def test_good_user_get_w_waitlist(self):
        wait_act = ActFactory(accepted=2,
                              b_conference=self.context.conference)
        self.context.book_act(wait_act)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assert_good_form_display(response)
        self.assertNotContains(response, wait_act.b_title)

    def test_good_user_get_show(self):
        login_as(self.privileged_profile, self)
        response = self.client.get("%s?show_id=%d" % (
            reverse(self.view_name, urlconf="gbe.scheduling.urls"),
            self.context.show.pk))
        self.assert_good_form_display(response)

    def test_good_user_post_success(self):
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_basic_post())
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        self.assertNotEqual(self.context.acts[0].b_title,
                            'changed title')
        self.assertNotEqual(str(self.context.acts[0].performer),
                            'changed performer')

    def test_good_user_post_success_w_label(self):
        self.context.order_act(self.context.acts[0], 2)
        login_as(self.privileged_profile, self)
        response = self.client.post(
            self.url,
            data=self.get_basic_post())
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        allocation = self.context.sched_event.resources_allocated.filter(
            ordering__class_id=self.context.acts[0].pk).first()
        self.assertEqual(allocation.ordering.order, 1)

    def test_good_user_get_success_w_label(self):
        self.context.order_act(self.context.acts[0], 2)
        login_as(self.privileged_profile, self)
        response = self.client.get(
            self.url)
        self.assert_good_form_display(response)
        allocation = self.context.sched_event.resources_allocated.filter(
            ordering__class_id=self.context.acts[0].pk).first()
        input_text = '<input type="number" name="%d-order" ' + \
                     'value="2" required id="id_%d-order" />'
        self.assertContains(
            response,
            input_text % (self.context.acts[0].pk, self.context.acts[0].pk),
            html=True)

    def test_good_user_post_invalid(self):
        login_as(self.privileged_profile, self)
        act, booking = self.context.book_act()
        data = self.get_basic_post()
        data['%d-performer' % act.pk] = 'changed performer'
        data['%d-title' % act.pk] = 'changed title'
        data['%d-booking_id' % act.pk] = booking.pk + 100
        data['%d-show' % act.pk] = 'bad'
        data['%d-order' % act.pk] = 'very bad'
        response = self.client.post(
            self.url,
            data=data)
        self.assertContains(response, '<ul class="errorlist">', 2)
        self.assertContains(response, 'Select a valid choice.')
        self.assertContains(response, 'Enter a whole number.')
        self.assertContains(
            response,
            ('<input type="hidden" name="%d-booking_id" value="%d" ' +
             'id="id_%d-booking_id">') % (
                self.context.acts[0].pk,
                data['%d-booking_id' % self.context.acts[0].pk],
                self.context.acts[0].pk), html=True)

    def test_good_user_change_show(self):
        new_show = ShowContext(conference=self.context.conference)
        rehearsal, slot = self.context.make_rehearsal()
        # this is a small hack - the show has an event label the rehearsal
        # doesn't
        booking = ResourceAllocationFactory(
            event=slot,
            resource=WorkerFactory(_item=self.context.acts[0].performer,
                                   role="Performer"))
        order = OrderingFactory(
            allocation=booking,
            class_id=self.context.acts[0].pk,
            class_name="Act")
        login_as(self.privileged_profile, self)
        data = self.get_basic_post()
        data['%d-show' % self.context.acts[0].pk] = str(
            new_show.sched_event.pk)

        response = self.client.post(
            self.url,
            data=data)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        self.assertEqual(new_show.sched_event.role_count("Performer"), 2)
        self.assertEqual(self.context.sched_event.role_count("Performer"), 0)
        self.assertFalse(
            ResourceAllocation.objects.filter(pk=booking.pk).exists())

    def test_good_user_get_only_conf_shows(self):
        not_this_conf_show = ShowFactory()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertNotContains(response, not_this_conf_show.e_title)
