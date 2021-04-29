from gbe.views import MakeBidView
from django.http import Http404
from django.urls import reverse
from gbe.forms import VendorBidForm
from gbe.models import (
    Business,
    Conference,
    Vendor,
    UserMessage
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

        self.businesses = self.owner.business_set.all()
        if self.businesses.count() == 0:
            return '%s?next=%s' % (
                reverse('business-add', urlconf='gbe.urls'),
                reverse('vendor_create', urlconf='gbe.urls'))

        if self.bid_object and (
                self.owner not in self.bid_object.business.owners.all()):
            raise Http404

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
                       'business': self.businesses[0],
                       'physical_address': self.owner.address}
        return initial

    def set_up_form(self):
        self.form.fields['business'].queryset = Business.objects.filter(
            owners=self.owner)

    def set_valid_form(self, request):
        self.bid_object.b_conference = self.conference
        self.bid_object = self.form.save()

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
