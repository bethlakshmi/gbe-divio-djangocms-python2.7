from django.db.models import (
    CharField,
    DateTimeField,
    Model,
    TextField,
    UniqueConstraint,
)


class StyleSelector(Model):
    selector = CharField(max_length=300)
    description = TextField(blank=True)
    pseudo_class = CharField(max_length=128, blank=True, null=True)
    target_element_usage = CharField(max_length=100)
    used_for = CharField(max_length=100)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        if self.pseudo_class:
            return ("%s:%s" % (self.selector, self.pseudo_class))
        else:
            return (self.selector)

    class Meta:
        app_label = "gbe"
        ordering = ['selector', 'pseudo_class']
        constraints = [UniqueConstraint(
            fields=['selector', 'pseudo_class'],
            name='unique_selector'),
        ]
