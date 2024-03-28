from django.forms import (
    CharField,
    EmailField,
)
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from gbe_forms_text import (
    user_form_help,
)
from django_recaptcha.fields import ReCaptchaField
from gbe.functions import check_forum_spam
from gbetext import (
    email_in_use_msg,
    found_on_list_msg,
)


class UserCreateForm(UserCreationForm):
    required_css_class = 'required'
    error_css_class = 'error'
    name = CharField(required=True, help_text=user_form_help['name'])
    email = EmailField(required=True)
    verification = ReCaptchaField()

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

    def save(self, commit=True):
        form = super(UserCreateForm, self).save(commit=False)
        form.username = form.email
        if commit:
            form.save()
        return form

    class Meta:
        model = User
        fields = ['email',
                  'name',
                  'password1',
                  'password2',
                  ]
