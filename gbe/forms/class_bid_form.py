from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ModelForm,
    MultipleChoiceField,
    Textarea,
)
from gbe.models import Class
from gbe_forms_text import (
    available_time_conflict,
    unavailable_time_conflict,
    classbid_help_texts,
    classbid_labels,
    class_schedule_options,
)
from tinymce.widgets import TinyMCE


class ClassBidDraftForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    schedule_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        required=False,
        label=classbid_labels['schedule_constraints']
    )
    avoided_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['avoided_constraints'],
        required=False)
    b_description = CharField(
        required=True,
        widget=TinyMCE(
            attrs={'cols': 80, 'rows': 20},
            mce_attrs={
                'theme_advanced_buttons1': "bold,italic,underline,|," +
                "justifyleft,justifycenter,justifyright,|,bullist,numlist,|," +
                "cut,copy,paste",
                'theme_advanced_buttons2': "",
                'theme_advanced_buttons3': "", }),
        label=classbid_labels['b_description'])

    class Meta:
        model = Class
        fields = ['b_title',
                  'teacher',
                  'b_description',
                  'maximum_enrollment',
                  'type',
                  'fee',
                  'length_minutes',
                  'history',
                  'schedule_constraints',
                  'avoided_constraints',
                  'space_needs']
        help_texts = classbid_help_texts
        labels = classbid_labels


class ClassBidForm(ClassBidDraftForm):
    schedule_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['schedule_constraints'])
    b_description = CharField(
        required=True,
        widget=TinyMCE(
            attrs={'cols': 80, 'rows': 20},
            mce_attrs={
                'theme_advanced_buttons1': "bold,italic,underline,|," +
                "justifyleft,justifycenter,justifyright,|,bullist,numlist,|," +
                "cut,copy,paste",
                'theme_advanced_buttons2': "",
                'theme_advanced_buttons3': "", }),
        label=classbid_labels['b_description'])

    def clean(self):
        cleaned_data = super(ClassBidForm, self).clean()
        conflict_windows = []
        if ('schedule_constraints' in self.cleaned_data) and (
                'avoided_constraints' in self.cleaned_data):
            conflict_windows = set(
                self.cleaned_data['schedule_constraints']).intersection(
                self.cleaned_data['avoided_constraints'])
        if len(conflict_windows) > 0:
            windows = ", ".join(
                class_schedule_options[int(w)][1] for w in conflict_windows)
            self._errors['schedule_constraints'] = \
                available_time_conflict % windows
            self._errors['avoided_constraints'] = \
                unavailable_time_conflict
        return cleaned_data
