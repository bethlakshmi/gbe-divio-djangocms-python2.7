from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ProfileFactory,
    ShowFactory,
)
from tests.factories.ticketing_factories import (
    BrownPaperEventsFactory,
    TransactionFactory,
)
from django.core.urlresolvers import reverse
from ticketing.models import BrownPaperEvents
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from gbetext import (
    link_event_to_ticket_success_msg,
    unlink_event_to_ticket_success_msg,
)


class TestEditBPTEvent(TestCase):
    '''Tests for bptevent_edit view'''

    def setUp(self):
        self.client = Client()
        self.bpt_event = BrownPaperEventsFactory()
        self.gbe_event = ShowFactory()
        self.privileged_user = ProfileFactory().user_object
        grant_privilege(self.privileged_user, 'Ticketing - Admin')
        self.url = reverse('set_ticket_to_event',
                           urlconf='ticketing.urls',
                           args=[self.bpt_event.bpt_event_id,
                                 "on",
                                 self.gbe_event.eventitem_id])

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
                str(self.bpt_event.conference.conference_slug),
                self.bpt_event.id))
        self.assertContains(response, link_event_to_ticket_success_msg)

    def test_set_link_off(self):
        self.bpt_event.linked_events.add(self.gbe_event)
        self.bpt_event.save()
        self.url = reverse('set_ticket_to_event',
                           urlconf='ticketing.urls',
                           args=[self.bpt_event.bpt_event_id,
                                 "off",
                                 self.gbe_event.eventitem_id])
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=ticket&updated_events=[%s]" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.bpt_event.conference.conference_slug),
                self.bpt_event.id))
        self.assertContains(response, unlink_event_to_ticket_success_msg)

    def test_bad_logic(self):
        self.url = reverse('set_ticket_to_event',
                           urlconf='ticketing.urls',
                           args=[self.bpt_event.bpt_event_id,
                                 "off",
                                 self.gbe_event.eventitem_id])
        login_as(self.privileged_user, self)
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(
            response,
            "%s?conference=%s&open_panel=ticket&updated_events=[%s]" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str(self.bpt_event.conference.conference_slug),
                self.bpt_event.id))
        self.assertNotContains(response, unlink_event_to_ticket_success_msg)
        self.assertNotContains(response, link_event_to_ticket_success_msg)
