from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render

from gbe_logging import log_func
from gbe.functions import (
    get_latest_conference,
    validate_perms,
)
from gbe.models import (
    Act,
    BidEvaluation,
    Conference,
    UserMessage,
)


class ReviewBidListView(View):
    bid_evaluation_type = BidEvaluation
    template = 'gbe/bid_review_list.tmpl'
    bid_order_fields = ('accepted', 'b_title')
    status_index = 4
    changed_id = -1

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        try:
            return super(ReviewBidListView, self).dispatch(*args, **kwargs)
        except IndexError:
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    def get_bids(self, request=None):
        return self.object_type.objects.filter(
            submitted=True,
            b_conference=self.conference).order_by(*self.bid_order_fields)

    def review_query(self, bids):
        return self.bid_evaluation_type.objects.filter(
            bid__in=bids).select_related(
                'evaluator').order_by('bid', 'evaluator')

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
            bid_row['status'] = "gbe-table-danger"
        elif bid.id == self.changed_id:
            bid_row['status'] = 'gbe-table-success'
        elif bid.ready_for_review:
            if not review_query.filter(
                        evaluator=self.reviewer,
                        bid=bid).exists():
                bid_row['bid'][self.status_index] = "Needs Review"
                bid_row['status'] = "gbe-table-info"
        return bid_row

    def get_rows(self, bids, review_query):
        rows = []
        for bid in bids:
            bid_row = self.set_row_basics(bid, review_query)
            bid_row['reviews'] = review_query.filter(
                bid=bid.id).select_related(
                    'evaluator').order_by(
                        'evaluator')
            rows.append(bid_row)
        return rows

    def get_bid_list(self, request=None):
        bids = self.get_bids(request)
        review_query = self.review_query(bids)
        self.rows = self.get_rows(bids, review_query)

    def groundwork(self, request):
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        bid_string = self.object_type().__class__.__name__
        self.page_title = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PAGE_TITLE",
                defaults={
                    'summary': "%s Page Title" % bid_string,
                    'description': 'Review %s' % bid_string})[0].description
        self.view_title = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="FIRST_HEADER",
                defaults={
                    'summary': "%s First Header" % bid_string,
                    'description': '%s Proposals' % bid_string
                    })[0].description
        self.user = request.user
        if request.GET.get('conf_slug'):
            self.conference = Conference.by_slug(request.GET['conf_slug'])
        else:
            self.conference = get_latest_conference()
        self.conference_slugs = Conference.all_slugs()

    def get_context_dict(self):
        context = {
            'conference': self.conference,
            'page_title': self.page_title,
            'view_title': self.view_title,
            'return_link': reverse(self.bid_review_list_view_name,
                                   urlconf='gbe.urls'),
            'conference_slugs': self.conference_slugs,
            'conference': self.conference,
            'columns': self.object_type().bid_review_header,
            'order': 0,
            'rows': self.rows}
        return context

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request)

        if request.GET.get('changed_id'):
            self.changed_id = int(request.GET['changed_id'])

        self.get_bid_list()

        return render(request,
                      self.template,
                      self.get_context_dict())

    @never_cache
    def post(self, request, *args, **kwargs):
        self.groundwork(request)
        self.get_bid_list(request)
        return render(request,
                      self.template,
                      self.get_context_dict())
