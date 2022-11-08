from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe_logging import log_func
from django.http import HttpResponseRedirect

from django.shortcuts import (
    render,
    get_object_or_404,
)
from gbe.models import UserMessage
from gbe.functions import validate_perms
from gbetext import (
    bid_not_submitted_msg,
    bid_not_paid_msg,
    default_submit_msg,
)
from gbe.ticketing_idd_interface import fee_paid
from django.urls import reverse


class ViewBidView(View):
    # Any view inheriting from this view should have an edit_view that
    # is named as "bidobject_edit" where the model BidObject is lower case
    performer = None

    def check_bid(self):
        return None

    def make_context(self):
        context = self.get_messages()
        context['readonlyform'] = self.get_display_forms()
        if self.performer:
            context['performer'] = self.performer
        return context

    def get_messages(self):
        context = {}
        if not self.bid.submitted:
            context['edit_url'] = reverse(
                "%s_edit" % self.bid.__class__.__name__.lower(),
                urlconf='gbe.urls',
                args=[self.bid.pk])
            is_fee_paid = False
            for profile in self.bid.profiles:
                if fee_paid(self.bid.__class__.__name__,
                            profile.user_object.username,
                            self.bid.b_conference):
                    is_fee_paid = True
                    break
            if is_fee_paid:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="UNSUBMITTED_PAID_BID",
                    defaults={
                        'summary': "No Payment Needed, Not Submitted Message",
                        'description': bid_not_submitted_msg})
            else:
                context['awaiting_payment'] = True
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="AWAITING_PAYMENT_BID",
                    defaults={
                        'summary': "Bid Awaits Payment - Wait for Refresh",
                        'description': bid_not_paid_msg})
            context['not_submit_message'] = user_message[0].description
        elif self.is_owner:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="BID_SUBMITTED",
                defaults={
                    'summary': "Thanks for submitting bid",
                    'description': default_submit_msg})
            context['submit_message'] = user_message[0].description
        bid_string = self.bid.__class__.__name__
        context['page_title'] = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PAGE_TITLE",
                defaults={
                    'summary': "%s Page Title" % bid_string,
                    'description': "Review %s Proposal" % bid_string
                    })[0].description
        context['view_title'] = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="FIRST_HEADER",
                defaults={
                    'summary': "%s First Header" % bid_string,
                    'description': "Review %s Proposal" % bid_string
                    })[0].description

        return context

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        bid_id = kwargs.get("bid_id")
        self.bid = get_object_or_404(self.bid_type, id=bid_id)
        redirect = self.check_bid()
        if redirect:
            return HttpResponseRedirect(redirect)

        self.is_owner = True
        if request.user.profile not in self.bid.profiles:
            validate_perms(request, self.viewer_permissions, require=True)
            self.is_owner = False

        return render(request, 'gbe/bid_view.tmpl', self.make_context())
