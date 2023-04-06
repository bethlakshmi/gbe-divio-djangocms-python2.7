from django.forms import (
    CharField,
    HiddenInput,
    ImageField,
    IntegerField,
    ModelForm,
    Textarea,
)
from gbe.models import Article
from gbe_forms_text import article_help_texts
from tempus_dominus.widgets import DatePicker


class ArticleForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Article
        fields = ['title',
                  'summary',
                  'content',
                  'slug',
                  'publish_status',
                  'live_as_of',
                  ]
        help_texts = article_help_texts
        widgets = {
        'content': Textarea(attrs={'id': 'user-tiny-mce'}),
        'live_as_of': DatePicker(
            attrs={'append': 'fa fa-calendar',
                   'icon_toggle': True},
            options={'format': "M/D/YYYY"})}
