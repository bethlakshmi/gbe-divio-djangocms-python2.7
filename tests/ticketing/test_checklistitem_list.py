from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.ticketing_factories import (
    RoleEligibilityConditionFactory,
    TicketItemFactory,
    TicketingEligibilityConditionFactory,
    TicketingEventsFactory,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
)
from gbetext import (
    intro_role_cond_message,
    intro_ticket_cond_message,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)


class TestCheckListItemList(TestCase):
    view_name = 'checklistitem_list'

    def setUp(self):
        self.client = Client()
        self.privileged_user = ProfileFactory.create().\
            user_object
        grant_privilege(self.privileged_user,
                        'Ticketing - Admin',
                        'view_checklistitem')
        self.url = reverse(self.view_name, urlconf='ticketing.urls')
        self.role_condition = RoleEligibilityConditionFactory()
        self.ticket_condition = TicketingEligibilityConditionFactory()
        self.ticket_item = TicketItemFactory()
        self.ticket_condition.tickets.add(self.ticket_item)

    def test_get_success(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        print(response)
        self.assertContains(response, intro_role_cond_message)
        self.assertContains(response, intro_ticket_cond_message)
        self.assertContains(response,
                            self.role_condition.checklistitem.description)
        self.assertContains(response,
                            self.ticket_condition.checklistitem.description)
        self.assertContains(response, self.role_condition.role)
        self.assertContains(response, self.ticket_item.title)
        self.assertContains(response, self.ticket_item.ticketing_event.title)
        self.assertContains(response, "No Override")
