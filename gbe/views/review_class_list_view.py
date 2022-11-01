from django.urls import reverse
from gbe.functions import validate_perms
from gbe.models import Class
from gbe.views import ReviewBidListView


class ReviewClassListView(ReviewBidListView):
    reviewer_permissions = ('Class Reviewers', )
    object_type = Class
    bid_review_view_name = 'class_review'
    bid_review_list_view_name = 'class_review_list'
    template = 'gbe/class_review_list.tmpl'
    page_title = 'Review Classes'
    view_title = 'Class Proposals'

    def set_row_basics(self, bid, review_query):
        bid_row = super(ReviewClassListView, self).set_row_basics(bid,
                                                                  review_query)
        if self.can_schedule:
            url = reverse("class_changestate",
                          urlconf='gbe.urls',
                          args=[bid.id])
            if bid.accepted == 3:
                bid_row['extra_button'] = {'url': url,
                                           'text': "Add to Schedule"}
            elif bid.ready_for_review:
                bid_row['extra_button'] = {'url': url,
                                           'text': "Accept & Schedule"}
        return bid_row

    def groundwork(self, request):
        self.can_schedule = validate_perms(request,
                                           ('Scheduling Mavens',),
                                           False)
