from django.db.models import (
    CASCADE,
    Model,
    ForeignKey,
    IntegerField,
    TextField,
)
from gbe.models import (
    Conference,
    Profile,
)
from gbetext import vote_options


class VolunteerEvaluation(Model):
    '''
    A response to a bid, cast by a privileged GBE staff member
    '''
    evaluator = ForeignKey(Profile,
                           on_delete=CASCADE,
                           related_name='evals_from')
    vote = IntegerField(choices=vote_options)
    notes = TextField(blank=True)
    volunteer = ForeignKey(Profile,
                           on_delete=CASCADE,
                           related_name='evals_for')
    conference = ForeignKey(
        Conference,
        on_delete=CASCADE)

    class Meta:
        app_label = "gbe"
        unique_together = (('evaluator', 'volunteer', 'conference'),)
        ordering = ["conference", "volunteer", 'evaluator']
