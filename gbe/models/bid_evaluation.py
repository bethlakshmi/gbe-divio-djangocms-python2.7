from django.db.models import (
    Model,
    ForeignKey,
    IntegerField,
    TextField,
)
from gbe.models import (
    Biddable,
    Profile,
)

from gbetext import vote_options


class BidEvaluation(Model):
    '''
    A response to a bid, cast by a privileged GBE staff member
    '''
    evaluator = ForeignKey(Profile)
    vote = IntegerField(choices=vote_options)
    notes = TextField(blank=True)
    bid = ForeignKey(Biddable)

    def __unicode__(self):
        return "%s: %s" % (self.bid.b_title, self.evaluator.display_name)

    class Meta:
        app_label = "gbe"
