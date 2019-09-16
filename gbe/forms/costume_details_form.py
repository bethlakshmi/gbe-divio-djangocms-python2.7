from django.forms import (
    CharField,
    ChoiceField,
    FileField,
    ModelForm,
    RadioSelect,
    Textarea,
    TypedChoiceField,
)
from gbe.models import Costume
from gbe_forms_text import (
    costume_proposal_help_texts,
    costume_proposal_labels,
)
from gbetext import boolean_options


class CostumeDetailsDraftForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    form_title = "Costume Information"

    pasties = TypedChoiceField(
        widget=RadioSelect,
        choices=boolean_options,
        label=costume_proposal_labels['pasties'],
        required=False)
    pieces = ChoiceField(choices=[(x, x) for x in range(1, 21)],
                         label=costume_proposal_labels['pieces'],
                         required=False)
    dress_size = ChoiceField(
        choices=[(x, x) for x in range(1, 21)],
        label=costume_proposal_labels['dress_size'],
        help_text=costume_proposal_help_texts['dress_size'],
        required=False)
    b_description = CharField(
        max_length=500,
        widget=Textarea,
        label=costume_proposal_labels['description'],
        required=False)
    more_info = CharField(
        max_length=500,
        widget=Textarea,
        label=costume_proposal_labels['more_info'],
        required=False)
    picture = FileField(
        label=costume_proposal_labels['picture'],
        help_text=costume_proposal_help_texts['picture'],
        required=False)

    class Meta:

        model = Costume
        fields = ['pieces',
                  'b_description',
                  'pasties',
                  'dress_size',
                  'more_info',
                  'picture']
        help_texts = costume_proposal_help_texts
        labels = costume_proposal_labels


class CostumeDetailsSubmitForm(CostumeDetailsDraftForm):

    pasties = TypedChoiceField(
        widget=RadioSelect,
        choices=boolean_options,
        label=costume_proposal_labels['pasties'])
    pieces = ChoiceField(
        choices=[(x, x) for x in range(1, 21)],
        label=costume_proposal_labels['pieces'])
    dress_size = ChoiceField(
        choices=[(x, x) for x in range(1, 21)],
        label=costume_proposal_labels['dress_size'],
        help_text=costume_proposal_help_texts['dress_size'])
    b_description = CharField(
        max_length=500,
        widget=Textarea,
        label=costume_proposal_labels['description'])
    picture = FileField(
        label=costume_proposal_labels['picture'],
        help_text=costume_proposal_help_texts['picture'])
