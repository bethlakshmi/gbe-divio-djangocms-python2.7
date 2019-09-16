from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe_logging import log_func
from django.http import HttpResponseRedirect

from django.shortcuts import (
    render,
    get_object_or_404,
)
from gbe.models import Vendor
from gbe.forms import (
    VendorBidForm,
    ParticipantForm,
)
from gbe.functions import validate_perms


class ViewBidView(View):
    performer = None

    def check_bid(self):
        return None

    def get_owner_profile(self):
        return self.bid.profile

    def make_context(self):
        display_forms = self.get_display_forms()
        context = {'readonlyform': display_forms, }
        if self.performer:
            context['performer'] = self.performer
        return context

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        bid_id = kwargs.get("bid_id")
        self.bid = get_object_or_404(self.bid_type, id=bid_id)
        redirect = self.check_bid()
        if redirect:
            return HttpResponseRedirect(redirect)

        self.owner_profile = self.get_owner_profile()
        if self.owner_profile != request.user.profile:
            validate_perms(request, self.viewer_permissions, require=True)
        return render(request, 'gbe/bid_view.tmpl', self.make_context())
