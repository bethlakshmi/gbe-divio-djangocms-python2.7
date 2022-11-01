from django.urls import reverse
from gbe.models import Costume
from gbe.views import ReviewBidListView


class ReviewCostumeListView(ReviewBidListView):
    bid_review_view_name = 'costume_review'
    bid_review_list_view_name = 'costume_review_list'
    object_type = Costume
    reviewer_permissions = ('Costume Reviewers', )
    page_title = 'Review Costumes'
    view_title = 'Costume Proposals'
