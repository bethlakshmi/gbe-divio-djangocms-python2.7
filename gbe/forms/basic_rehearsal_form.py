from django.forms import (
    CharField,
    ChoiceField,
    HiddenInput,
    Form,
    ModelMultipleChoiceField,
    MultipleHiddenInput,
)
from gbe.models import (
    Profile,
    UserMessage,
)
from dal import autocomplete
from django.urls import reverse_lazy
from django.core.validators import MaxLengthValidator
from gbetext import membership_help


class BasicRehearsalForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'

    booking_id = CharField(widget=HiddenInput, required=False)
    rehearsal = ChoiceField()
    membership = ModelMultipleChoiceField(
        queryset=Profile.objects.filter(user_object__is_active=True),
        widget=autocomplete.ModelSelect2Multiple(
            url=reverse_lazy('profile-autocomplete', urlconf='gbe.urls'),
            attrs={'data-minimum-input-length': 3}))

    def __init__(self, *args, **kwargs):
        act = None
        if 'act' in kwargs:
            act = kwargs.pop('act')
        super(BasicRehearsalForm, self).__init__(*args, **kwargs)

        num_performers = 1
        if act is not None and act.num_performers:
            num_performers = act.num_performers
        self.fields['membership'].validators = [MaxLengthValidator(
            num_performers)]
        if num_performers > 1:
            membership_msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="MEMBERSHIP_HELP_TEXT",
                defaults={'summary': "Act performer select help text",
                          'description': membership_help})

            self.fields['membership'].help_text = (
                membership_msg[0].description + "  Choose up to %d performers"
                ) % num_performers
        else:
            self.fields['membership'].widget = MultipleHiddenInput()

    class Meta:
        fields = ['booking_id', 'rehearsal']
