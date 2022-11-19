from django.db.models import (
    CASCADE,
    ForeignKey,
    Model,
    IntegerField,
)

from gbe.models import (
    Act,
    Show,
)
from gbetext import vote_options


class ShowVote(Model):

    show = ForeignKey(Show,
                      on_delete=CASCADE,
                      blank=True,
                      null=True)
    vote = IntegerField(choices=vote_options,
                        blank=True,
                        null=True)

    class Meta:
        verbose_name = "show vote"
        verbose_name_plural = "show votes"
        app_label = "gbe"
