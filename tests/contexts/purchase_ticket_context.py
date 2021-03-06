from tests.factories.gbe_factories import (
    ConferenceFactory,
    ProfileFactory
)
from tests.factories.ticketing_factories import (
    TransactionFactory,
)


class PurchasedTicketContext:

    def __init__(self, profile=None):
        self.transaction = TransactionFactory(
            ticket_item__ticketing_event__badgeable=True
        )
        if profile:
            self.profile = profile
            # the order of setting this line matters - see test_reports - BB
            self.transaction.purchaser.matched_to_user = \
                self.profile.user_object
            self.transaction.purchaser.save()
        else:
            self.profile = ProfileFactory(
                user_object=self.transaction.purchaser.matched_to_user
            )
        self.conference = self.transaction.ticket_item.ticketing_event.conference
