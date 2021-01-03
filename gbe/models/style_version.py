from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    Model,
)
from django.core.validators import MinValueValidator
from decimal import Decimal


class StyleVersion(Model):
    name = CharField(max_length=128)
    number = DecimalField(decimal_places=3,
                          max_digits=12,
                          validators=[MinValueValidator(Decimal('0.00'))])
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    currently_live = BooleanField(default=False)
    currently_test = BooleanField(default=False)

    def __str__(self):
        return ("{} - version {:.1f}".format(self.name, self.number))

    class Meta:
        app_label = "gbe"
        ordering = ['name', 'number']
        unique_together = [['name', 'number']]

    def save(self, *args, **kwargs):
        if self.currently_live:
            # select all other active items
            qs = type(self).objects.filter(currently_live=True)
            # except self (if self already exists)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # and deactive them
            qs.update(currently_live=False)
        if self.currently_test:
            # select all other active items
            qs = type(self).objects.filter(currently_test=True)
            # except self (if self already exists)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # and deactive them
            qs.update(currently_test=False)

        super(StyleVersion, self).save(*args, **kwargs)
