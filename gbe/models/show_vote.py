from django.db.models import (
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
                      blank=True,
                      null=True)
    vote = IntegerField(choices=vote_options,
                        blank=True,
                        null=True)

    def __str__(self):
        return "<ShowVote %s - %s>" % (str(self.show), str(self.vote))

    class Meta:
        verbose_name = "show vote"
        verbose_name_plural = "show votes"
        app_label = "gbe"
