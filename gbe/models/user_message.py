from django.db import models


class UserMessage(models.Model):
    summary = models.CharField(max_length=128)
    description = models.TextField(max_length=3000)
    view = models.CharField(max_length=128)
    code = models.CharField(max_length=128)

    def __str__(self):
        return "%s: %s" % (self.view, self.code)

    class Meta:
        app_label = "gbe"
        unique_together = (('view', 'code'),)
