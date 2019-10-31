from aldryn_client import forms

class Form(forms.BaseForm):
    paginator_paginate_by = forms.CharField('Paginator: item per page count', required=False)

    def to_settings(self, data, settings):
        settings['ALDRYN_COMMON_PAGINATOR_PAGINATE_BY'] = data['paginator_paginate_by']
        return settings
