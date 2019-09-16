from django.forms import (
    BooleanField,
    CharField,
    ChoiceField,
    Form,
    RadioSelect,
    Textarea,
)
from gbe.models import Class
from gbetext import new_grade_options


class EventEvaluationForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    def __init__(self, *args, **kwargs):
        questions = None
        if 'questions' in kwargs:
            questions = kwargs.pop('questions')
        super(EventEvaluationForm, self).__init__(*args, **kwargs)
        for question in questions:
            if question.answer_type == "text":
                self.fields['question%d' % question.id] = CharField(
                    label=question.question,
                    help_text=question.help_text,
                    widget=Textarea,
                    required=False
                )
            if question.answer_type == "grade":
                self.fields['question%d' % question.id] = ChoiceField(
                    label=question.question,
                    help_text=question.help_text,
                    choices=new_grade_options,
                    widget=RadioSelect,
                )
            if question.answer_type == "boolean":
                self.fields['question%d' % question.id] = BooleanField(
                    label=question.question,
                    help_text=question.help_text,
                    required=False
                )
