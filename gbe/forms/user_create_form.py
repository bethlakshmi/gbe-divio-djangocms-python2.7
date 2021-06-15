from django.forms import (
    CharField,
    EmailField,
    ModelForm,
)
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gbe_forms_text import (
    username_help,
    username_label,
)
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget
from gbe.functions import check_forum_spam


class UserCreateForm(UserCreationForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = EmailField(required=True)
    username = CharField(label=username_label, help_text=username_help)
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    verification = ReCaptchaField(widget=ReCaptchaWidget())

    def is_valid(self):
        valid = super(UserCreateForm, self).is_valid()

        if valid:
            email = self.cleaned_data['email']
            if User.objects.filter(email__iexact=email).count():
                self._errors['email'] = 'That email address is already in use'
                valid = False
            elif check_forum_spam(self.cleaned_data['email']):
                self._errors['email'] = 'That email address is not accepted'
                valid = False 
        return valid

    class Meta:
        model = User
        fields = ['username',
                  'email',
                  'first_name',
                  'last_name',
                  'password1',
                  'password2',
                  ]
