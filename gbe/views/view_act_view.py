from django.urls import reverse
from gbe.models import (
    Act,
)
from gbe.views import ViewBidView


class ViewActView(ViewBidView):

    bid_type = Act
    viewer_permissions = ('Act Reviewers',)
    bid_prefix = "The Act"

    def make_context(self):
        context = self.get_messages()
        context.update({
            'performer': self.bid.performer,
            'act': self.bid,
            'display_contact_info': True})
        return context
