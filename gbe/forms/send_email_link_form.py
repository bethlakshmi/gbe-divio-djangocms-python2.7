from django.forms import (
    EmailField,
    Form,
)
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget


class SendEmailLinkForm(Form):
    email = EmailField(required=True)
    verification = ReCaptchaField(widget=ReCaptchaWidget(), label="")
