from django.forms import (
    CharField,
    IntegerField,
    HiddenInput,
    ModelChoiceField,
    ModelForm,
    NumberInput,
    TextInput,
)
from gbe.models import (
    StyleProperty,
    StyleValue,
    UserMessage,
)
from gbe_forms_text import (
    theme_help,
    style_value_help,
)


class StyleValueForm(ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'
    style_property = ModelChoiceField(widget=HiddenInput(),
                                      queryset=StyleProperty.objects.all())

    class Meta:
        model = StyleValue
        fields = ['style_property']

    def __init__(self, *args, **kwargs):
        # there's some thought-crud here in that "template" used to mean 
        # the value type, while now "template" means the layout including
        # CSS syntax the user doesn't see.  Changed the code, but not the 
        # UserMessages
        style_property = None
        if 'initial' in kwargs and 'style_property' in kwargs.get('initial'):
            style_property = kwargs.get('initial')['style_property']

        super(StyleValueForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            instance = kwargs.get('instance')
            style_property = instance.style_property
            values = instance.parseable_values.split()
        elif style_property:
            values = kwargs.get('initial')['value'].split()
        else:
            raise Exception(UserMessage.objects.get_or_create(
                view="StyleValueForm",
                code="CANNOT_INSTANTIATE",
                defaults={
                    'summary': "Theme Setup Error",
                    'description': theme_help['no_args']})[0].description)
        i = 0
        value_set = style_property.value_type.split()
        if len(value_set) != len(values):
            user_msg = UserMessage.objects.get_or_create(
                view="StyleValueForm",
                code="TEMPLATE_VALUE_MISMATCH",
                defaults={
                    'summary': "Property Template Does Not Match Value",
                    'description': theme_help['mismatch']})
            raise Exception("%s, VALUES: %s, TEMPLATE: %s" % (
                user_msg[0].description,
                values,
                value_set))
        for value_type_item, value in zip(value_set, values):
            help_text = None
            help_key = "%s-%d" % (style_property.style_property, i)
            if help_key in style_value_help:
                help_text = style_value_help[help_key]
            if value_type_item == "rgba":
                self.fields['value_%d' % i] = CharField(
                    widget=TextInput(attrs={'data-jscolor': ''}),
                    initial=value,
                    label="color",
                    help_text=help_text)
            elif value_type_item == "px":
                self.fields['value_%d' % i] = IntegerField(
                    initial=int(value),
                    label="pixels",
                    help_text=help_text,
                    widget=NumberInput(attrs={'class': 'pixel-input'}))
            else:
                user_msg = UserMessage.objects.get_or_create(
                    view="StyleValueForm",
                    code="UNKNOWN_TEMPLATE_ELEMENT",
                    defaults={
                        'summary': "Parse Template Error",
                        'description': theme_help['bad_elem']})
                raise Exception("%s, VALUES: %s" % (user_msg[0].description,
                                                    style_property.value_type))
            i = i + 1

    def save(self, commit=True):
        style_value = super(StyleValueForm, self).save(commit=False)
        i = 0
        value = ""
        value_string = ""
        val_list = []
        val_prop = style_value.style_property
        for value_type_item in val_prop.value_type.split():
            value = value + str(self.cleaned_data['value_%d' % i]) + " "
            val_list += [str(self.cleaned_data['value_%d' % i])]
            i = i + 1

        style_value.parseable_values = value.strip()
        style_value.value = val_prop.value_template.format(*val_list)
        if commit:
            style_value.save()
        return style_value
