from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import(
    ConferenceFactory,
    ProfileFactory,
)
from tests.factories.ticketing_factories import (
    PurchaserFactory,
    TicketingEventsFactory,
    TicketItemFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
    make_act_app_ticket,
)
from gbetext import create_comp_msg
from gbe_utils.text import no_permission_msg


class TestIndex(TestCase):
    '''Tests for index view'''
    view_name = 'home'

    def setUp(self):
        self.client = Client()
        # Conference Setup
        conference = ConferenceFactory(accepting_bids=True, status='upcoming')
        self.ticketing_event = TicketingEventsFactory(
            conference=conference,
            act_submission_event=True)
        self.ticket = TicketItemFactory(
            ticket_id="%s-1111" % (self.ticketing_event.event_id),
            ticketing_event=self.ticketing_event,
            special_comp=True)

        # User/Human setup
        self.profile = ProfileFactory()
        self.privileged_user = ProfileFactory()
        grant_privilege(self.privileged_user, 'Ticketing - Transactions')

        self.url = reverse("comp_ticket", urlconf="ticketing.urls")

    def test_get_only_special_form(self):
        reg_ticket = TicketItemFactory(
            ticket_id="%s-22222" % (self.ticketing_event.event_id),
            ticketing_event=self.ticketing_event,
            special_comp=False)
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertNotContains(
            response,
            str(reg_ticket.title))
        self.assertContains(
            response,
            str(self.ticket))
        self.assertContains(
            response,
            '<a href="%s" class="btn gbe-btn-light">Cancel</a>' % (
                reverse('transactions', urlconf="ticketing.urls")),
            html=True)

    def test_get_w_next(self):
        login_as(self.privileged_user, self)
        response = self.client.get("%s?next=/next/something" % self.url)
        self.assertContains(
            response,
            '<a href="/next/something" class="btn gbe-btn-light">Cancel</a>',
            html=True)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))
        self.assertContains(response, no_permission_msg)

    def test_make_purchaser(self):
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={
            'ticket_item': self.ticket.pk,
            'profile': self.profile.pk,
            }, follow=True)
        self.assertEqual(self.profile.user_object.purchaser_set.count(), 1)
        buyer = self.profile.user_object.purchaser_set.first()
        self.assertRedirects(
            response,
            "%s?changed_id=%d" % (
                reverse("transactions", urlconf="ticketing.urls"),
                buyer.transaction_set.first().pk))
        self.assertContains(response, create_comp_msg)

    def test_bad_form(self):
        login_as(self.privileged_user, self)
        response = self.client.post(self.url, data={
            'ticket_item': self.ticket.pk+1,
            'profile': self.profile.pk,
            })
        self.assertContains(response, "Select a valid choice.")

    def test_have_purchaser_use_next(self):
        act_review_url = reverse("act_review_list", urlconf="gbe.urls")
        grant_privilege(self.privileged_user, 'Act Reviewers')

        buyer = PurchaserFactory(matched_to_user=self.profile.user_object)
        login_as(self.privileged_user, self)
        response = self.client.post(
            "%s?next=%s" % (self.url, act_review_url),
            data={'ticket_item': self.ticket.pk,
                  'profile': self.profile.pk},
            follow=True)
        self.assertEqual(self.profile.user_object.purchaser_set.count(), 1)
        self.assertRedirects(
            response,
            "%s?changed_id=%d" % (
                act_review_url,
                buyer.transaction_set.first().pk))
