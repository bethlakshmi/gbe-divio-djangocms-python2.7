from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from ticketing.models import (
    TicketItem,
)
from tests.factories.ticketing_factories import(
    TicketItemFactory,
)
from django.contrib.admin.sites import AdminSite


class SchedulerChangeListTests(TestCase):
    def setUp(self):
        self.client = Client()
        password = 'mypassword'
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', password)
        self.client.login(
            username=self.privileged_user.username,
            password=password)

    def test_get_ticketitem_active(self):
        ticket = TicketItemFactory(live=True, has_coupon=False)
        response = self.client.get('/admin/ticketing/ticketitem/')
        assert "True" in response.content

    def test_get_eventcontainer_conference(self):
        ticket = TicketItemFactory()
        response = self.client.get('/admin/ticketing/ticketitem/')
        assert str(ticket.bpt_event.conference) in response.content
