from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    Model,
    UniqueConstraint,
    SET_NULL,
)
from gbe.models import (
    StyleElement,
    StyleLabel,
    StyleSelector,
)


class StyleProperty(Model):
    selector = ForeignKey(StyleSelector, on_delete=CASCADE)
    label = ForeignKey(StyleLabel, on_delete=SET_NULL, null=True, blank=True)
    element = ForeignKey(StyleElement,
                         on_delete=SET_NULL,
                         null=True,
                         blank=True)
    hidden = BooleanField(default=False)
    style_property = CharField(max_length=300)
    value_type = CharField(max_length=128)
    value_template = CharField(max_length=128,
                               default="default")
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
