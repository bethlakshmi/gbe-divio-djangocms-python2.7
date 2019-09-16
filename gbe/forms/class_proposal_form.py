from django.forms import (
    CharField,
    ModelForm,
    Textarea,
)
from gbe.models import ClassProposal
from gbe_forms_text import (
    class_proposal_help_texts,
    class_proposal_labels,
)


class ClassProposalForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    proposal = CharField(
        max_length=500,
        widget=Textarea,
        help_text=class_proposal_help_texts['proposal'],
        label=class_proposal_labels['proposal'])

    class Meta:
        model = ClassProposal
        fields = ['name', 'title', 'type', 'proposal']
        required = ['title']
        help_texts = class_proposal_help_texts
        labels = class_proposal_labels
