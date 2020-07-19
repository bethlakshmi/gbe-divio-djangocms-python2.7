from django.db.models import (
    CASCADE,
    Model,
    CharField,
    ForeignKey,
)
from gbe.models import Act
from gbetext import (
    festival_list,
    festival_experience,
)


class PerformerFestivals(Model):
    festival = CharField(max_length=20, choices=festival_list)
    experience = CharField(max_length=20,
                           choices=festival_experience,
                           default='No')
    act = ForeignKey(Act, on_delete=CASCADE)

    class Meta:
        verbose_name_plural = 'performer festivals'
        app_label = "gbe"
