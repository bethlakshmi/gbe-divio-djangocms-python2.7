from django.forms import (
    CharField,
    ModelForm,
    RadioSelect,
    TypedChoiceField,
    TextInput,
)
from gbe.models import Costume
from gbe_forms_text import (
    costume_proposal_help_texts,
    costume_proposal_labels,
)
from gbetext import boolean_options


class CostumeBidDraftForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    active_use = TypedChoiceField(
        widget=RadioSelect,
        choices=boolean_options,
        label=costume_proposal_labels['active_use'],
        required=False)
    debut_date = CharField(
        label=costume_proposal_labels['debut_date'],
        help_text=costume_proposal_help_texts['debut_date'],
        widget=TextInput(attrs={'placeholder': 'MM/YYYY'}),
        required=False)

    class Meta:
        model = Costume
        fields = ['b_title',
                  'performer',
                  'creator',
                  'act_title',
                  'debut_date',
                  'active_use']
        help_texts = costume_proposal_help_texts
        labels = costume_proposal_labels


class CostumeBidSubmitForm(CostumeBidDraftForm):
    active_use = TypedChoiceField(
        widget=RadioSelect,
        choices=boolean_options,
        label=costume_proposal_labels['active_use'])
