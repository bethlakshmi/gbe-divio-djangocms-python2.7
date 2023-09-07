from django.forms import (
    CharField,
    ChoiceField,
    HiddenInput,
    Form,
    ModelMultipleChoiceField,
)
from gbe.models import Profile
from dal import autocomplete
from django.urls import reverse_lazy


class BasicRehearsalForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    booking_id = CharField(widget=HiddenInput, required=False)
    rehearsal = ChoiceField()
    membership = ModelMultipleChoiceField(
        queryset=Profile.objects.filter(user_object__is_active=True),
        widget=autocomplete.ModelSelect2Multiple(
            url=reverse_lazy('profile-autocomplete', urlconf='gbe.urls'),
            attrs={
                'data-minimum-input-length': 3,
                },))

    def __init__(self, *args, **kwargs):
        super(BasicRehearsalForm, self).__init__(*args, **kwargs)

    class Meta:
        fields = ['booking_id', 'rehearsal']
