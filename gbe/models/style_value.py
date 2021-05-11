from django.db.models import (
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    Model,
    UniqueConstraint,
)
from gbe.models import (
    MetaColor,
    StyleProperty,
    StyleVersion,
)
from filer.fields.image import FilerImageField
from django.core.validators import MaxValueValidator, MinValueValidator


class StyleValue(Model):
    style_property = ForeignKey(StyleProperty, on_delete=CASCADE)
    style_version = ForeignKey(StyleVersion, on_delete=CASCADE)
    meta_color = ForeignKey(MetaColor, on_delete=CASCADE, null=True)
    value = CharField(max_length=200, null=True)
    opacity = DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        validators=[
            MaxValueValidator(1.0),
            MinValueValidator(0)])
    image = FilerImageField(
        on_delete=CASCADE,
        null=True)

    class Meta:
        app_label = "gbe"
        ordering = ['style_version', 'style_property']
        constraints = [UniqueConstraint(
            fields=['style_property', 'style_version'],
            name='unique_value'),
        ]
