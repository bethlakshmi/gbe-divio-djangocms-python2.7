from django.urls import reverse
from django.contrib.auth.models import Group
from django.test import TestCase
from django.test.client import RequestFactory
from django.test import Client
from ticketing.views import ticket_item_edit
from tests.factories import gbe_factories, ticketing_factories
from tests.functions.gbe_functions import (
    location,
    login_as,
)


class TestEditTicketItem(TestCase):
    '''Tests for ticket_item_edit view'''
    view_name = 'ticket_item_edit'

    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.ticketitem = ticketing_factories.TicketItemFactory.create()
        group, created = Group.objects.get_or_create(name='Ticketing - Admin')
        self.privileged_user = gbe_factories.ProfileFactory.create().\
            user_object
        self.privileged_user.groups.add(group)
        self.url = reverse(
            self.view_name,
            args=[self.ticketitem.pk],
            urlconf='ticketing.urls')

    def get_ticketitem_form(self):
        return {
                'ticket_id': "333333-444444",
                'title': "Title from Form",
                'live': False,
                'cost': 1.01,
                'bpt_event': self.ticketitem.bpt_event.pk
        }

    def test_edit_ticket_user_is_not_ticketing(self):
        '''
            The user does not have the right privileges.  Send PermissionDenied
        '''
        user = gbe_factories.ProfileFactory.create().user_object
        login_as(user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_edit_ticket_bad_ticketitem(self):
        '''
           Unknown ticket item submitted by valid user, should have an error
           and resend same form (status 200)
        '''
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.view_name,
            args=[200],
            urlconf='ticketing.urls'), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_get_new_ticketitem(self):
        '''
           good user gets new ticket form, all is good.
        '''
        login_as(self.privileged_user, self)
        response = self.client.get(reverse(
            self.view_name,
            urlconf='ticketing.urls'))
        self.assertEqual(response.status_code, 200)

    def test_edit_ticketitem(self):
        '''
           good user gets form to edit existing ticket, all is good.
        '''
        self.ticketitem.save()
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ticket_edit_post_form_all_good(self):
        '''
            Good form, good user, return the main edit page
        '''
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data=self.get_ticketitem_form())
        conf_slug = self.ticketitem.bpt_event.conference.conference_slug

        self.assertEqual(response.status_code, 302)
        assert '/ticketing/ticket_items?conference=%s' % conf_slug in location(
            response)

    def test_ticket_add_post_form_all_good(self):
        '''
            Good form, good user, return the main edit page
        '''
        new_ticket = self.get_ticketitem_form()
        request = self.factory.post('/ticketing/ticket_item_edit/',
                                    new_ticket)
        request.user = self.privileged_user
        response = ticket_item_edit(request)
        conf_slug = self.ticketitem.bpt_event.conference.conference_slug

        self.assertEqual(response.status_code, 302)
        self.assertEqual(location(response),
                         '/ticketing/ticket_items?conference=%s' % conf_slug)

    def test_ticket_edit_post_form_bad_bptevent(self):
        '''
            Invalid form data submitted, fail with error and return form
        '''
        error_form = self.get_ticketitem_form()
        error_form['bpt_event'] = -1
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data=error_form)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Ticketing')
        self.assertContains(response, error_form.get('title'))

    def test_ticket_form_delete(self):
        '''
            Good form, good user, delete item and return to main page
        '''
        delete_ticket = self.get_ticketitem_form()
        delete_ticket['delete_item'] = ''
        delete_me = ticketing_factories.TicketItemFactory.create()
        delete_me.ticket_id = "444444-555555"
        delete_me.save()
        conf_slug = delete_me.bpt_event.conference.conference_slug
        delete_url = reverse(
            self.view_name,
            args=[delete_me.pk],
            urlconf='ticketing.urls')
        login_as(self.privileged_user, self)
        response = self.client.post(
            delete_url,
            data=delete_ticket)
        self.assertEqual(response.status_code, 302)
        assert '/ticketing/ticket_items?conference=%s' % conf_slug in location(
            response)

    def test_ticket_form_delete_missing_item(self):
        '''
            Good form, good user, delete item that doesn't exist - get an error
        '''
        self.url = reverse(
            self.view_name,
            args=[self.ticketitem.pk+1],
            urlconf='ticketing.urls')
        delete_ticket = self.get_ticketitem_form()
        delete_ticket['delete_item'] = ''
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data=delete_ticket,
            follow=True)
        self.assertEqual(response.status_code, 404)

    def test_delete_ticket_with_transactions(self):
        '''
            Attempt to delete a ticket item that has a transaction
            Get a failure, return to edit page
        '''
        delete_ticket = self.get_ticketitem_form()
        delete_ticket['delete_item'] = ''
        transaction = ticketing_factories.TransactionFactory.create()
        transaction.save()
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            data=delete_ticket)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Edit Ticketing')
        self.assertContains(response, 'Cannot remove Ticket')
