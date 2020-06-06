from gbe.forms import (
    SummerActForm,
)
from gbe.views import ViewActView


class ViewSummerActView(ViewActView):

    object_form_type = SummerActForm
    bid_prefix = "The Summer Act"
    edit_name = "summer_act_edit"
