from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    Model,
    UniqueConstraint,
)
from gbe.models import StyleVersion


class MetaColor(Model):
    style_version = ForeignKey(StyleVersion, on_delete=CASCADE)
    value = CharField(max_length=200)
    name = CharField(max_length=200)

    def str(self):
        return self.name

    class Meta:
        app_label = "gbe"
        ordering = ['name']
        constraints = [UniqueConstraint(
            fields=['style_version', 'name'],
            name='unique_meta_name'),
        ]
