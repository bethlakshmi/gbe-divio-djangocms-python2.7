from django.db.models import (
    EmailField,
    Model,
    OneToOneField,
)
from post_office.models import EmailTemplate


class EmailTemplateSender(Model):
    template = OneToOneField(EmailTemplate, related_name="sender")
    from_email = EmailField()

    class Meta:
        ordering = ['template__name']
        app_label = "gbe"
