from django.forms import (
    EmailField,
    Form,
)
from django_recaptcha.fields import ReCaptchaField


class SendEmailLinkForm(Form):
    email = EmailField(required=True)
    verification = ReCaptchaField(label="")
