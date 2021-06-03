from tests.factories.ticketing_factories import (
    TicketingEventsFactory,
    PayPalSettingsFactory,
    TicketItemFactory,
)


def setup_fees(conference, is_act=False, is_vendor=False):
    PayPalSettingsFactory()
    event = TicketingEventsFactory(conference=conference,
                                    vendor_submission_event=is_vendor,
                                    act_submission_event=is_act)
    if is_vendor:
        ticket = TicketItemFactory(live=True, ticketing_event=event)
        add_on = TicketItemFactory(live=True,
                                   ticketing_event=event,
                                   add_on=True)
        return [ticket, add_on]
    if is_act:
        ticket = TicketItemFactory(live=True,
                                   ticketing_event=event,
                                   is_minimum=True,
                                   cost=10)
        return [ticket]
