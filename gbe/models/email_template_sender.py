from django.db.models import (
    CASCADE,
    EmailField,
    Model,
    OneToOneField,
)
from post_office.models import EmailTemplate


class EmailTemplateSender(Model):
    template = OneToOneField(EmailTemplate,
                             on_delete=CASCADE,
                             related_name="sender")
    from_email = EmailField()

    class Meta:
        ordering = ['template__name']
        app_label = "gbe"
