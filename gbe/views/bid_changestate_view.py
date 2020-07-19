from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from django.http import HttpResponseRedirect
from gbe_logging import log_func
from gbe.models import (
    Biddable,
    UserMessage,
)
from gbe.forms import BidStateChangeForm
from gbe.functions import validate_perms
from gbe.email.functions import send_bid_state_change_mail
from gbetext import bidder_email_fail_msg


class BidChangeStateView(View):
    bid_state_change_form = BidStateChangeForm
    next_page = None

    @log_func
    def bid_state_change(self, request):
        form = self.bid_state_change_form(request.POST, instance=self.object)
        if form.is_valid():
            self.object = form.save()
        else:
            return render(
                request,
                'gbe/bid_review.tmpl',
                {'actionform': False,
                 'actionURL': False})
        return HttpResponseRedirect(self.next_page)

    def get_object(self, request, object_id):
        self.object = get_object_or_404(self.object_type,
                                        id=object_id)

    def prep_bid(self, request, args, kwargs):
        object_id = kwargs['object_id']
        self.get_object(request, object_id)
        self.get_bidder()
        self.reviewer = validate_perms(request, self.coordinator_permissions)

    def notify_bidder(self, request):
        if str(self.object.accepted) != request.POST['accepted']:
            email_status = send_bid_state_change_mail(
                str(self.object_type.__name__).lower(),
                self.bidder.contact_email,
                self.bidder.get_badge_name(),
                self.object,
                int(request.POST['accepted']))
            self.check_email_status(request, email_status)

    def check_email_status(self, request, email_status):
        if email_status:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="EMAIL_FAILURE",
                defaults={
                    'summary': "Email Failed",
                    'description': bidder_email_fail_msg})
            messages.error(
                request,
                user_message[0].description)

    def groundwork(self, request, args, kwargs):
        self.next_page = reverse(self.redirectURL, urlconf='gbe.urls')
        self.prep_bid(request, args, kwargs)
        self.notify_bidder(request)

    @log_func
    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return self.bid_state_change(request)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(BidChangeStateView, self).dispatch(*args, **kwargs)
