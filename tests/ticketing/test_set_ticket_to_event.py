from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import ProfileFactory
from tests.factories.ticketing_factories import (
    TicketingEventsFactory,
    TicketTypeFactory,
    TransactionFactory,
)
from django.urls import reverse
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import (
    link_event_to_ticket_success_msg,
    unlink_event_to_ticket_success_msg,
)
from tests.factories.scheduler_factories import SchedEventFactory
from scheduler.models import Event
from django.db.models import Max


class TestSetTicketToEvent(TestCase):
    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.ticketing_event = TicketingEventsFactory()
        cls.gbe_event = SchedEventFactory()
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Ticketing - Admin')
        cls.url = reverse('set_ticket_to_event',
                          urlconf='ticketing.urls',
                          args=[cls.ticketing_event.pk,
                                cls.ticketing_event.__class__.__name__,
                                "on",
                                cls.gbe_event.pk])
        cls.url_off = reverse('set_ticket_to_event',
                              urlconf='ticketing.urls',
                              args=[cls.ticketing_event.pk,
                                    cls.ticketing_event.__class__.__name__,
                                    "off",
                                    cls.gbe_event.pk])

    def test_use_user_is_not_ticketing(self):
        user = ProfileFactory.create().user_object
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertEqual(403, response.status_code)

    def test_set_link_on(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=ticket&updated_events=[%s]" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.ticketing_event.conference.conference_slug),
                self.ticketing_event.id))
        self.assertContains(response, link_event_to_ticket_success_msg)

    def test_set_link_on_ticket_type(self):
        ticket_type = TicketTypeFactory(
            ticketing_event__source=3,
            ticketing_event__conference=self.ticketing_event.conference)
        login_as(self.privileged_user, self)
        url = reverse('set_ticket_to_event',
                      urlconf='ticketing.urls',
                      args=[ticket_type.pk,
                            ticket_type.__class__.__name__,
                            "on",
                            self.gbe_event.pk])
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=ticket&updated_events=[%s]" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.ticketing_event.conference.conference_slug),
                ticket_type.id))
        self.assertContains(response, link_event_to_ticket_success_msg)

    def test_bad_class_name(self):
        ticket_type = TicketTypeFactory(
            ticketing_event__source=3,
            ticketing_event__conference=self.ticketing_event.conference)
        login_as(self.privileged_user, self)
        url = reverse('set_ticket_to_event',
                      urlconf='ticketing.urls',
                      args=[ticket_type.pk,
                            "BadClassName",
                            "on",
                            self.gbe_event.pk])
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_set_link_off(self):
        self.ticketing_event.linked_events.add(self.gbe_event)
        self.ticketing_event.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url_off, follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=ticket&updated_events=[%s]" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.ticketing_event.conference.conference_slug),
                self.ticketing_event.id))
        self.assertContains(response, unlink_event_to_ticket_success_msg)

    def test_bad_logic(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url_off, follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=ticket&updated_events=[%s]" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.ticketing_event.conference.conference_slug),
                self.ticketing_event.id))
        self.assertNotContains(response, unlink_event_to_ticket_success_msg)
        self.assertNotContains(response, link_event_to_ticket_success_msg)

    def test_bad_sched_event(self):
        bad_pk = Event.objects.aggregate(Max('pk'))['pk__max']+1
        self.url = reverse('set_ticket_to_event',
                           urlconf='ticketing.urls',
                           args=[self.ticketing_event.pk,
                                 self.ticketing_event.__class__.__name__,
                                 "off",
                                 bad_pk])
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertEqual(404, response.status_code)
