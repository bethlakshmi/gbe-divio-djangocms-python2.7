from django.urls import reverse
from gbe.forms import (
    ActEditForm,
)
from gbe.models import (
    Act,
)
from gbe.views import ViewBidView
from gbe.views.act_display_functions import get_act_form


class ViewActView(ViewBidView):

    bid_type = Act
    viewer_permissions = ('Act Reviewers',)
    object_form_type = ActEditForm
    bid_prefix = "The Act"

    def check_bid(self):
        if self.bid and self.bid.b_conference.act_style == "summer" and (
                self.__class__.__name__ != "ViewSummerActView"):
            return reverse(
                'summeract_view',
                urlconf='gbe.urls',
                args=[self.bid.pk])
        elif self.bid and not self.bid.b_conference.act_style == "summer" and (
                self.__class__.__name__ == "ViewSummerActView"):
            return reverse(
                'act_view',
                urlconf='gbe.urls',
                args=[self.bid.pk])
        return None

    def get_display_forms(self):
        actform = get_act_form(
            self.bid,
            self.object_form_type,
            self.bid_prefix)
        self.performer = self.bid.performer
        return (actform, )
