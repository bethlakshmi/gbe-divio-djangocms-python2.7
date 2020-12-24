from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    Model,
    UniqueConstraint,
)
from gbe.models import (
    StyleProperty,
    StyleVersion,
)


class StyleValue(Model):
    style_property = ForeignKey(StyleProperty, on_delete=CASCADE)
    style_version = ForeignKey(StyleVersion, on_delete=CASCADE)
    value = CharField(max_length=200)

    class Meta:
        app_label = "gbe"
        ordering = ['style_version', 'style_property']
        constraints = [UniqueConstraint(
            fields=['style_property', 'style_version'],
            name='unique_value'),
        ]
