from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    IntegerField,
    Model,
    TextField,
    UniqueConstraint,
)
from gbe.models import StyleGroup


class StyleElement(Model):
    name = CharField(max_length=128)
    group = ForeignKey(StyleGroup, on_delete=CASCADE)
    description = TextField(blank=True)
    order = IntegerField()
    sample_html = TextField(blank=True)

    def __str__(self):
        return ("%s - %s" % (self.group, self.name))

    class Meta:
        app_label = "gbe"
        ordering = ['group', 'name']
        constraints = [UniqueConstraint(fields=['name', 'group'],
                                        name='element_unique_name'), 
                       UniqueConstraint(fields=['order', 'group'],
                                        name='element_unique_order')]
