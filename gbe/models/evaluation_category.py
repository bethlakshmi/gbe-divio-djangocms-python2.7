from django.db.models import (
    BooleanField,
    CharField,
    Model,
    TextField,
)


class EvaluationCategory(Model):
    category = CharField(
        max_length=128,
        unique=True)
    visible = BooleanField(default=True)
    help_text = TextField(blank=True)

    def __str__(self):
        return self.category

    class Meta:
        app_label = "gbe"
        verbose_name_plural = 'Evaluation Categories'
        ordering = ['category', ]
