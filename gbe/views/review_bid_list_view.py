from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render

from gbe_logging import log_func
from gbe.functions import validate_perms
from gbe.models import (
    Act,
    BidEvaluation,
    Conference,
)


class ReviewBidListView(View):
    bid_evaluation_type = BidEvaluation
    template = 'gbe/bid_review_list.tmpl'
    bid_order_fields = ('accepted', 'b_title')
    status_index = 4

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewBidListView, self).dispatch(*args, **kwargs)

    def get_bids(self):
        return self.object_type.objects.filter(
            submitted=True,
            b_conference=self.conference).order_by(*self.bid_order_fields)

    def review_query(self, bids):
        return self.bid_evaluation_type.objects.filter(
            bid__in=bids).select_related(
                'evaluator').order_by('bid', 'evaluator')

    def row_hook(self, bid, row):
        # override on subclass
        pass

    def set_row_basics(self, bid, review_query):
        bid_row = {
            'bid': bid.bid_review_summary,
            'id': bid.id,
            'review_url': reverse(self.bid_review_view_name,
                                  urlconf='gbe.urls',
                                  args=[bid.id]),
            'status': "",
        }
        if not bid.bidder_is_active:
            bid_row['status'] = "danger"
        elif bid.id == self.changed_id:
            bid_row['status'] = 'success'
        elif bid.ready_for_review:
            if not review_query.filter(
                        evaluator=self.reviewer,
                        bid=bid).exists():
                bid_row['bid'][self.status_index] = "Needs Review"
                bid_row['status'] = "info"
        return bid_row

    def get_rows(self, bids, review_query):
        rows = []
        for bid in bids:
            bid_row = self.set_row_basics(bid, review_query)
            bid_row['reviews'] = review_query.filter(
                bid=bid.id).select_related(
                    'evaluator').order_by(
                        'evaluator')
            self.row_hook(bid, bid_row)
            rows.append(bid_row)
        return rows

    def get_bid_list(self):
        bids = self.get_bids()
        review_query = self.review_query(bids)
        self.rows = self.get_rows(bids, review_query)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        self.user = request.user
        if request.GET.get('conf_slug'):
            self.conference = Conference.by_slug(request.GET['conf_slug'])
        else:
            self.conference = Conference.current_conf()

        if request.GET.get('changed_id'):
            self.changed_id = int(request.GET['changed_id'])
        else:
            self.changed_id = -1

        try:
            self.get_bid_list()
        except IndexError:
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

        self.conference_slugs = Conference.all_slugs()

        return render(request, self.template,
                      self.get_context_dict())
