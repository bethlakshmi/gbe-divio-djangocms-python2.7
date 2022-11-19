from django.forms import (
    BooleanField,
    IntegerField,
    HiddenInput,
    TextInput,
)
from gbe_forms_text import (
    classbid_help_texts,
    classbid_labels,
)
from gbe.scheduling.forms import EventBookingForm


class ClassBookingForm(EventBookingForm):
    accepted = IntegerField(
        initial=3,
        widget=HiddenInput)
    submitted = BooleanField(widget=HiddenInput, initial=True)

    class Meta:
        fields = ['type',
                  'title',
                  'slug',
                  'description',
                  'maximum_enrollment',
                  'fee',
                  'accepted',
                  'submitted',
                  'eventitem_id',
                  ]
        help_texts = classbid_help_texts
        labels = classbid_labels
