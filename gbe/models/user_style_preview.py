from django.db.models import (
    CASCADE,
    Model,
    OneToOneField,
    ForeignKey,
)
from gbe.models import StyleVersion
from django.contrib.auth.models import User


class UserStylePreview(Model):
    version = ForeignKey(StyleVersion, on_delete=CASCADE)
    previewer = OneToOneField(User, on_delete=CASCADE)

    class Meta:
        app_label = "gbe"
