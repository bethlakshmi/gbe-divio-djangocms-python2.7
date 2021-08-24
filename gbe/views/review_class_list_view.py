from django.urls import reverse
from gbe.models import Class
from gbe.views import ReviewBidListView


class ReviewClassListView(ReviewBidListView):
    reviewer_permissions = ('Class Reviewers', )
    object_type = Class
    bid_review_view_name = 'class_review'
    bid_review_list_view_name = 'class_review_list'
    template = 'gbe/class_review_list.tmpl'

    def set_row_basics(self, bid, review_query):
        bid_row = super(ReviewClassListView, self).set_row_basics(bid,
                                                                  review_query)
        if bid.accepted == 3:
            bid_row['extra_button'] = {
                'url': reverse("class_changestate",
                               urlconf='gbe.urls',
                               args=[bid.id]),
                'text': "Add to Schedule",
            }
        elif bid.ready_for_review:
            bid_row['extra_button'] = {
                'url': reverse("class_changestate",
                               urlconf='gbe.urls',
                               args=[bid.id]),
                'text': "Accept & Schedule",
            }
        return bid_row


    def get_context_dict(self):
        return {'columns': self.object_type().bid_review_header,
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference,
                'order': 0}
