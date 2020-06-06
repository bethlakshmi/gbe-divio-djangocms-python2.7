from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe_logging import log_func
from django.http import HttpResponseRedirect

from django.shortcuts import (
    render,
    get_object_or_404,
)
from gbe.models import (
    UserMessage,
    Vendor,
)
from gbe.forms import (
    VendorBidForm,
    ParticipantForm,
)
from gbe.functions import validate_perms
from gbetext import (
    bid_not_submitted_msg,
    bid_not_paid_msg,
)
from gbe.ticketing_idd_interface import fee_paid
from django.core.urlresolvers import reverse


class ViewBidView(View):
    performer = None

    def check_bid(self):
        return None

    def get_owner_profile(self):
        return self.bid.profile

    def make_context(self):
        display_forms = self.get_display_forms()
        paid = fee_paid(self.bid.__class__.__name__,
                        self.owner_profile.user_object.username,
                        self.bid.b_conference)
        context = {'readonlyform': display_forms,
                   'paid': paid}
        if self.performer:
            context['performer'] = self.performer
        if not self.bid.submitted:
            context['edit_url'] = reverse(
                self.edit_name,
                urlconf='gbe.urls',
                args=[self.bid.pk])
            if paid:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="UNSUBMITTED_PAID_BID",
                    defaults={
                        'summary': "No Payment Needed, Not Submitted Message",
                        'description': bid_not_submitted_msg})
            else:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="AWAITING_PAYMENT_BID",
                    defaults={
                        'summary': "Bid Awaits Payment - Wait for Refresh",
                        'description': bid_not_paid_msg})                
            context['not_submitted_message'] = user_message[0].description
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
