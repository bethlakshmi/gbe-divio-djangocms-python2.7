from django.forms import (
    ChoiceField,
    Form,
)
from gbetext import act_shows_options_short


class BidBioMergeForm(Form):
    required_css_class = 'required'
    error_css_class = 'error'
    bio_fields = []

    def __init__(self, *args, **kwargs):
        super(BidBioMergeForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs and 'otherprofile' in kwargs.get(
                    'initial') and 'targetprofile' in kwargs.get('initial'):
            otherprofile = kwargs.get('initial').get('otherprofile')
            targetprofile = kwargs.get('initial').get('targetprofile')
            bio_choices = [('','Move to Merged Profile')] + [
                (target.pk, 
                 str(target)) for target in targetprofile.bio_set.all()]
            for bio in otherprofile.bio_set.all():
                self.fields['bio_%d' % bio.pk] = ChoiceField(
                    choices=bio_choices,
                    label=str(bio),
                    required=False,
                )
                self.bio_fields += ['bio_%d' % bio.pk]
        else:
            raise Exception(kwargs)
