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
from gbetext import (
    email_in_use_msg,
    found_on_list_msg,
)


class UserCreateForm(UserCreationForm):
    required_css_class = 'required'
    error_css_class = 'error'
    email = EmailField(required=True)
    username = CharField(label=username_label, help_text=username_help)
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    verification = ReCaptchaField(widget=ReCaptchaWidget())

    def is_valid(self):
        from gbe.models import UserMessage
        valid = super(UserCreateForm, self).is_valid()

        if valid:
            email = self.cleaned_data['email']
            if User.objects.filter(email__iexact=email).count():
                self._errors['email'] = UserMessage.objects.get_or_create(
                    view="RegisterView",
                    code="EMAIL_IN_USE",
                    defaults={
                        'summary': "User with Email Exists",
                        'description': email_in_use_msg
                        })[0].description
                valid = False
            elif check_forum_spam(self.cleaned_data['email']):
                self._errors['email'] = UserMessage.objects.get_or_create(
                    view="RegisterView",
                    code="FOUND_IN_FORUMSPAM",
                    defaults={
                        'summary': "User on Stop Forum Spam",
                        'description': found_on_list_msg
                        })[0].description
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
