from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory
)
from tests.factories.ticketing_factories import (
    TransactionFactory,
)


class PurchasedTicketContext:

    def __init__(self, profile=None, conference=None):
        self.conference = conference or ConferenceFactory()
        self.profile = profile or ProfileFactory()
        self.transaction = TransactionFactory(
            ticket_item__ticketing_event__badgeable=True,
            ticket_item__ticketing_event__conference=self.conference,
            purchaser__matched_to_user=self.profile.user_object,
        )
