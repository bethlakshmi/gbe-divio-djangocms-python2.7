from django.core.urlresolvers import reverse
from django.test import (
    Client,
    TestCase
)
from tests.factories.gbe_factories import (
    ActFactory,
    ProfileFactory,
    ShowFactory
)
from scheduler.models import EventItem
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
            resource__actresource___item=self.context.acts[0]).first()
        data = {
            '%d-performer' %
            self.context.acts[0].resourceitem_id: 'changed performer',
            '%d-title' %
            self.context.acts[0].resourceitem_id: 'changed title',
            '%d-booking_id' %
            self.context.acts[0].resourceitem_id: allocation.pk,
            '%d-show' %
            self.context.acts[0].resourceitem_id: str(
                self.context.sched_event.pk),
            '%d-order' % self.context.acts[0].resourceitem_id: 1}
        return data

    def assert_good_form_display(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<ul class="errorlist">', response.content)
        for act in self.context.acts:
            if act.accepted == 3:
                self.assertContains(response, act.b_title)
                self.assertContains(response, str(act.performer))
            else:
                self.assertNotContains(response, act.b_title)
                self.assertNotContains(response, str(act.performer))
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

    def test_good_user_get_success(self):
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assert_good_form_display(response)

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
        self.assertIn('bgcolor="red"', response.content)

    def test_good_user_get_two_shows_same_title(self):
        ShowFactory(e_title=self.context.show.e_title)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assert_good_form_display(response)

    def test_good_user_get_success_not_scheduled(self):
        show = ShowFactory()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('<ul class="errorlist">', response.content)
        self.assertIn('Performer', response.content)

    def test_good_user_get_w_waitlist(self):
        wait_act = ActFactory(accepted=2,
                              b_conference=self.context.conference)
        self.context.book_act(wait_act)
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assert_good_form_display(response)

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
            resource__actresource___item=self.context.acts[0]).first()
        self.assertEqual(allocation.ordering.order, 1)

    def test_good_user_get_success_w_label(self):
        self.context.order_act(self.context.acts[0], 2)
        login_as(self.privileged_profile, self)
        response = self.client.get(
            self.url)
        self.assert_good_form_display(response)
        allocation = self.context.sched_event.resources_allocated.filter(
            resource__actresource___item=self.context.acts[0]).first()
        input_text = '<input type="number" name="%d-order" ' + \
                     'value="2" required id="id_%d-order" />'
        self.assertContains(
            response,
            input_text % (self.context.acts[0].resourceitem_id,
                          self.context.acts[0].resourceitem_id))

    def test_good_user_post_invalid(self):
        login_as(self.privileged_profile, self)
        data = self.get_basic_post()
        data['%d-show' % self.context.acts[0].resourceitem_id] = 'bad'
        data['%d-order' % self.context.acts[0].resourceitem_id] = 'very bad'
        data['%d-booking_id' % self.context.acts[0].resourceitem_id] = \
            'adfasdfasdfkljasdfklajsdflkjasdlkfjalksjdflkasjdflkjasdl'
        response = self.client.post(
            self.url,
            data=data)
        self.assertContains(response, '<ul class="errorlist">', 2)
        self.assertContains(response, 'Select a valid choice.')
        self.assertContains(response, 'Enter a whole number.')

    def test_good_user_change_show(self):
        new_show = ShowContext(conference=self.context.conference)
        login_as(self.privileged_profile, self)
        data = self.get_basic_post()
        data['%d-show' % self.context.acts[0].resourceitem_id] = str(
            new_show.sched_event.pk)

        response = self.client.post(
            self.url,
            data=data)
        self.assertRedirects(
            response,
            reverse('home', urlconf='gbe.urls'))
        self.assertEqual(new_show.sched_event.volunteer_count, "2 acts")
        self.assertEqual(self.context.sched_event.volunteer_count, 0)

    def test_good_user_get_only_conf_shows(self):
        not_this_conf_show = ShowFactory()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        assert not_this_conf_show.e_title not in response.content
