from django.forms import (
    BooleanField,
    IntegerField,
    HiddenInput,
    TextInput,
)
from gbe.models import Class
from gbe_forms_text import (
    classbid_help_texts,
    classbid_labels,
)
from gbe.scheduling.forms import EventBookingForm


class ClassBookingForm(EventBookingForm):
    accepted = IntegerField(
        initial=3,
        widget=HiddenInput)
    eventitem_id = IntegerField(
        widget=HiddenInput,
        required=False)
    submitted = BooleanField(widget=HiddenInput, initial=True)

    def save(self, commit=True):
        this_class = super(ClassBookingForm, self).save(commit=False)
        this_class.b_title = this_class.e_title
        if commit:
            this_class.save()
        return this_class

    class Meta:
        model = Class
        fields = ['type',
                  'e_title',
                  'slug',
                  'e_description',
                  'maximum_enrollment',
                  'fee',
                  'accepted',
                  'submitted',
                  'eventitem_id',
                  ]
        help_texts = classbid_help_texts
        labels = classbid_labels
