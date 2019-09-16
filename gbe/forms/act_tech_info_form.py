from django.forms import (
    ModelForm,
)
from gbe.models import Act
from gbe.expoformfields import FriendlyURLInput
from gbe_forms_text import (
    act_bid_labels,
)


class ActTechInfoForm(ModelForm):
    form_title = "Act Tech Info"
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Act
        fields = ['b_title',
                  'b_description',
                  'performer',
                  'video_link',
                  'video_choice']
        widgets = {'video_link': FriendlyURLInput}
        labels = act_bid_labels
