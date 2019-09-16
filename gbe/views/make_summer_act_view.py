from gbe.views import MakeActView
from gbe.forms import (
    SummerActDraftForm,
    SummerActForm,
)
from gbe_forms_text import summer_act_popup_text


class MakeSummerActView(MakeActView):
    view_title = 'Propose an Act for The MiniExpo'
    submit_form = SummerActForm
    draft_form = SummerActDraftForm

    def make_context(self):
        context = super(MakeActView, self).make_context()
        context['popup_text'] = summer_act_popup_text
        return context
