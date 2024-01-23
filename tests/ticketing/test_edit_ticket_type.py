from django.urls import reverse
from django.test import TestCase
from tests.factories.gbe_factories import ProfileFactory
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.ticketing_factories import (
    TicketTypeFactory,
    TransactionFactory,
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    SchedEventFactory,
)
from ticketing.models import TicketType


class TestEditTicketType(TestCase):
    '''Tests for ticket_item_edit view'''
    view_name = 'ticket_type_update'

    @classmethod
    def setUpTestData(cls):
        cls.ticketitem = TicketTypeFactory(ticketing_event__source=3)
        cls.event = SchedEventFactory()
        cls.other_event = SchedEventFactory()
        EventLabelFactory(
            event=cls.event,
            text=cls.ticketitem.ticketing_event.conference.conference_slug)
        EventLabelFactory(
            event=cls.other_event,
            text=cls.ticketitem.ticketing_event.conference.conference_slug)
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Ticketing - Admin')
        cls.url = reverse(
            cls.view_name,
            args=[cls.ticketitem.pk],
            urlconf='ticketing.urls')

    def get_ticketitem_form(self):
        return {
                'ticket_id': self.ticketitem.ticket_id,
                'title': "Title from Form",
                'live': False,
                'cost': 1.01,
                'ticketing_event': self.ticketitem.ticketing_event.pk,
                'linked_events': []
        }

    def test_edit_ticket_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Send PermissionDenied
        '''
        user = ProfileFactory.create().user_object
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('home', urlconf="gbe.urls"))

    def test_edit_ticketitem(self):
        '''
           good user gets form to edit existing ticket, all is good.
        '''
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertContains(response, 'Edit Ticket Type')
        self.assertContains(response, reverse(
            "ticket_item_edit",
            urlconf="ticketing.urls",
            args=[self.ticketitem.pk]) + "?delete_item=True")
        self.assertContains(response, self.event.title)

    def test_ticket_edit_post_form(self):
        '''
            Good form, good user, return the main edit page
        '''
        login_as(self.privileged_user, self)
        data = self.get_ticketitem_form()
        response = self.client.post(
            self.url,
            data=data,
            follow=True)

        self.assertRedirects(
            response,
            "%s?updated_tickets=%s&open_panel=ticket" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str([self.ticketitem.id])))

    def test_ticket_edit_change_linked_event(self):
        '''
            Testing for the bug on linked event editing, where the event
            didn't actually get saved.
        '''
        login_as(self.privileged_user, self)
        data = self.get_ticketitem_form()
        data['linked_events'] = [self.other_event.pk]
        response = self.client.post(
            self.url,
            data=data,
            follow=True)
        self.assertRedirects(
            response,
            "%s?updated_tickets=%s&open_panel=ticket" % (
                reverse('ticket_items', urlconf='ticketing.urls'),
                str([self.ticketitem.id])))
        refresh_ticket = TicketType.objects.get(pk=self.ticketitem.pk)
        self.assertEqual(refresh_ticket.linked_events.count(), 1)
        self.assertEqual(refresh_ticket.linked_events.first().pk,
                         self.other_event.pk)
