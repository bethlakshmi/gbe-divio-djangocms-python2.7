import factory
from factory import (
    Sequence,
    SubFactory
)
from factory.django import DjangoModelFactory
import ticketing.models as tickets
import gbe.models as conf
from tests.factories.gbe_factories import (
    ConferenceFactory,
    UserFactory
)
from django.utils import timezone
from tests.factories.scheduler_factories import SchedEventFactory


class TicketingEventsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketingEvents
    title = Sequence(lambda x: "title #%d" % x)
    description = "This is a desription"
    event_id = Sequence(lambda x: "%d" % x)
    conference = SubFactory(ConferenceFactory)
    act_submission_event = False
    vendor_submission_event = False
    include_conference = False
    include_most = False
    ticket_style = Sequence(lambda x: "TicketingEventsTicketStyle #%d" % x)
    source = 1


class EventbriteSettingsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.EventbriteSettings
    oauth = "UseAMock"
    organization_id = "12345678"
    system = 1
    active_sync = True


class HumanitixSettingsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.HumanitixSettings
    api_key = "UseAMock"
    organiser_id = "12345678"
    system = 1
    active_sync = True
    endpoint = "test.an.endpoint"


class TicketItemFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketItem
    ticketing_event = SubFactory(TicketingEventsFactory)
    ticket_id = "111111-222222"
    title = Sequence(lambda x: "Ticket Item #%d" % x)
    cost = 99.99
    modified_by = "Ticket Item Mock"


class TicketTypeFactory(TicketItemFactory):
    class Meta:
        model = tickets.TicketType


class TicketPackageFactory(TicketItemFactory):
    class Meta:
        model = tickets.TicketPackage
    whole_shebang = True


class PurchaserFactory(DjangoModelFactory):
    class Meta:
        model = tickets.Purchaser
    first_name = Sequence(lambda x: "purchaser_first: #%d" % x)
    last_name = Sequence(lambda x: "purchaser_last: #%d" % x)
    email = Sequence(lambda x: "purchaser_%d@test.com" % x)
    phone = "111-222-3333"
    matched_to_user = SubFactory(UserFactory)


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.Transaction
    ticket_item = SubFactory(TicketItemFactory)
    purchaser = SubFactory(PurchaserFactory)
    amount = 99.99
    order_date = timezone.now()
    reference = Sequence(lambda x: "reference: #%d" % x)
    payment_source = Sequence(lambda x: "payment_source: #%d" % x)
    import_date = timezone.now()


class PayPalSettingsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.PayPalSettings
    business_email = Sequence(lambda x: "%duser@email.com" % x)


class CheckListItemFactory(DjangoModelFactory):
    class Meta:
        model = tickets.CheckListItem
    description = Sequence(lambda x: "Check List Item: #%d" % x)


class TicketingEligibilityConditionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketingEligibilityCondition

    checklistitem = SubFactory(CheckListItemFactory)

    @factory.post_generation
    def tickets(self, create, extracted, **kwargs):
        if extracted:
            # A list of groups were passed in, use them
            for ticket in extracted:
                self.tickets.add(ticket)


class RoleEligibilityConditionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleEligibilityCondition

    checklistitem = SubFactory(CheckListItemFactory)
    role = "Teacher"


class SignatureFactory(DjangoModelFactory):
    class Meta:
        model = tickets.Signature
    name_signed = Sequence(lambda x: "Signature %d" % x)
    conference = SubFactory(ConferenceFactory)
    user = SubFactory(UserFactory)


class TicketingExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketingExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)

    @factory.post_generation
    def tickets(self, create, extracted, **kwargs):
        if extracted:
            # A list of groups were passed in, use them
            for ticket in extracted:
                self.tickets.add(ticket)


class RoleExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)
    role = "Teacher"
    event = SubFactory(SchedEventFactory)


class NoEventRoleExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)
    role = "Teacher"
