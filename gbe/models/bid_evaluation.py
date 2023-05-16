from django.db.models import (
    CASCADE,
    Model,
    ForeignKey,
    IntegerField,
    TextField,
)
from gbe.models import (
    Account,
    Biddable,
    Profile,
)

from gbetext import vote_options


class BidEvaluation(Model):
    '''
    A response to a bid, cast by a privileged GBE staff member
    '''
    evaluator = ForeignKey(Profile, on_delete=CASCADE)
    evaluator_acct = ForeignKey(Account, on_delete=CASCADE, null=True)
    vote = IntegerField(choices=vote_options)
    notes = TextField(blank=True)
    bid = ForeignKey(Biddable, on_delete=CASCADE)

    class Meta:
        app_label = "gbe"
