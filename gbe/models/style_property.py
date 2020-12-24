from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    Model,
    ForeignKey,
    UniqueConstraint,
)
from gbe.models import StyleSelector


class StyleProperty(Model):
    selector = ForeignKey(StyleSelector, on_delete=CASCADE)
    style_property = CharField(max_length=300)
    value_type = CharField(
        max_length=128,
        choices=[('color', 'color')],
        default='color')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return ("%s - %s" % (self.selector, self.style_property))

    class Meta:
        app_label = "gbe"
        ordering = ['selector', 'style_property']
        verbose_name_plural = 'style properties'
        constraints = [UniqueConstraint(
            fields=['selector', 'style_property'],
            name='unique_property'),
        ]
