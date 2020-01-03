from gbe.views import MakeBidView
from django.http import Http404
from gbe.ticketing_idd_interface import (
    performer_act_submittal_link,
    verify_performer_app_paid,
)
from gbe.forms import VendorBidForm
from gbe.models import (
    Conference,
    Vendor,
    UserMessage
)
from gbe.ticketing_idd_interface import (
    vendor_submittal_link,
    verify_vendor_app_paid,
)
from gbetext import (
    default_vendor_submit_msg,
    default_vendor_draft_msg
)


class MakeVendorView(MakeBidView):
    page_title = 'Vendor Application'
    view_title = 'Vendor Application'
    submit_fields = ['b_title',
                     'b_description',
                     'physical_address',
                     ]
    draft_fields = submit_fields
    bid_type = "Vendor"
    has_draft = True
    submit_msg = default_vendor_submit_msg
    draft_msg = default_vendor_draft_msg
    submit_form = VendorBidForm
    draft_form = VendorBidForm
    prefix = 'thebiz'
    bid_class = Vendor

    def groundwork(self, request, args, kwargs):
        redirect = super(
            MakeVendorView,
            self).groundwork(request, args, kwargs)
        if redirect:
            return redirect

        if self.bid_object and (self.bid_object.profile != self.owner):
            raise Http404
        self.fee_link = vendor_submittal_link(request.user.id)

    def get_initial(self):
        initial = {}
        if self.bid_object:
            if len(self.bid_object.help_times.strip()) > 0:
                help_times_initial = eval(self.bid_object.help_times)
            else:
                help_times_initial = []
            initial = {'help_times': help_times_initial}
        else:
            initial = {'profile': self.owner,
                       'physical_address': self.owner.address}
        return initial

    def make_context(self, request):
        context = super(MakeVendorView, self).make_context(request)
        context['fee_link'] = self.fee_link
        return context

    def set_valid_form(self, request):
        self.bid_object.b_conference = self.conference
        self.bid_object = self.form.save()

    def fee_paid(self):
        return verify_vendor_app_paid(
            self.owner.user_object.username,
            self.conference)

    def make_post_forms(self, request, the_form):
        if self.bid_object:
            self.form = the_form(
                request.POST,
                request.FILES,
                instance=self.bid_object,
                initial=self.get_initial(),
                prefix=self.prefix)
        else:
            self.form = the_form(
                request.POST,
                request.FILES,
                initial=self.get_initial(),
                prefix=self.prefix)
