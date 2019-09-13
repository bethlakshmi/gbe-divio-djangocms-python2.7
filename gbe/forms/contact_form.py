from django.forms import (
    CharField,
    EmailField,
    Form,
    Textarea,
)


class ContactForm(Form):
    '''Form for managing user contacts. Notice that there
    are no models associated with this form.
    '''
    name = CharField(required=True)
    email = EmailField(required=True)
    subject = CharField(required=True)
    message = CharField(widget=Textarea)
