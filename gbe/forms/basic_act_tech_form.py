from django.forms import (
    CharField,
    DurationField,
    IntegerField,
    Form,
    Textarea,
)
from gbe_forms_text import (
    act_help_texts,
    tech_labels,
    tech_help_texts,
)

class BasicActTechForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    length_of_act = DurationField(help_text=act_help_texts['act_duration'])
    introduction_text = CharField(
        required=False,
        help_text=act_help_texts['intro_text'],
        widget=Textarea())
    feel_of_act = CharField(
        label=tech_labels['feel_of_act'],
        help_text=tech_help_texts['feel_of_act'],
        widget=Textarea())
    costume_colors = CharField(
        label=tech_labels['costume'],
        widget=Textarea())
    preset = CharField(
        required=False,
        label=tech_labels['preset'],
        help_text=tech_help_texts['preset'],
        widget=Textarea())
    remove = CharField(
        required=False,
        label=tech_labels['remove'],
        help_text=tech_help_texts['remove'],
        widget=Textarea())
