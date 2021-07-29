from django.db.models import (
    CASCADE,
    CharField,
    IntegerField,
    Model,
    ForeignKey,
    UniqueConstraint,
)
from gbe.models import StyleGroup


class StyleLabel(Model):
    name = CharField(max_length=128)
    group = ForeignKey(StyleGroup, on_delete=CASCADE)
    help_text = CharField(max_length=500)
    order = IntegerField()

    def __str__(self):
        return ("%s - %s" % (self.group, self.name))

    class Meta:
        app_label = "gbe"
        ordering = ['group__order', 'order']
        constraints = [UniqueConstraint(fields=['name', 'group'],
                                        name='label_unique_name'), 
                       UniqueConstraint(fields=['order', 'group'],
                                        name='label_unique_order')]
