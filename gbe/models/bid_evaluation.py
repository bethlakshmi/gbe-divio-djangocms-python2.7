from django.db.models import (
    CASCADE,
    Model,
    ForeignKey,
    IntegerField,
    TextField,
)
from gbe.models import (
    Profile,
    Biddable,
    Profile,
)

from gbetext import vote_options


class BidEvaluation(Model):
    '''
    A response to a bid, cast by a privileged GBE staff member
    '''
    evaluator = ForeignKey(Profile, on_delete=CASCADE)
    vote = IntegerField(choices=vote_options)
    notes = TextField(blank=True)
    bid = ForeignKey(Biddable, on_delete=CASCADE)

    class Meta:
        app_label = "gbe"
