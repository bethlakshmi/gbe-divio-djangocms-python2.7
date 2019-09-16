from django.core.urlresolvers import reverse
from gbe.models import Class
from review_bid_list_view import ReviewBidListView


class ReviewClassListView(ReviewBidListView):
    reviewer_permissions = ('Class Reviewers', )
    object_type = Class
    bid_review_view_name = 'class_review'
    bid_review_list_view_name = 'class_review_list'

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}
