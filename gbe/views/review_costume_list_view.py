from django.core.urlresolvers import reverse
from gbe.models import Costume
from gbe.views import ReviewBidListView


class ReviewCostumeListView(ReviewBidListView):
    bid_review_view_name = 'costume_review'
    bid_review_list_view_name = 'costume_review_list'
    object_type = Costume
    reviewer_permissions = ('Costume Reviewers', )

    def get_bids(self):
        return self.object_type.objects.filter(
            submitted=True,
            b_conference=self.conference).order_by(
                'accepted',
                'b_title')

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}
