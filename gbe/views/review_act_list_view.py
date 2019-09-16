from django.core.urlresolvers import reverse
from gbe.models import (
    Act,
    ActBidEvaluation,
    EvaluationCategory,
    FlexibleEvaluation,
)
from review_bid_list_view import ReviewBidListView
from django.db.models import Avg


class ReviewActListView(ReviewBidListView):
    reviewer_permissions = ('Act Reviewers', )
    object_type = Act
    bid_evaluation_type = ActBidEvaluation
    template = 'gbe/act_bid_review_list.tmpl'
    bid_review_view_name = 'act_review'
    bid_review_list_view_name = 'act_review_list'
    bid_order_fields = ('accepted', 'performer')
    status_index = 3

    def get_context_dict(self):
        return {'header': self.object_type().bid_review_header,
                'categories': EvaluationCategory.objects.filter(
                    visible=True).order_by('category'),
                'rows': self.rows,
                'return_link': reverse(self.bid_review_list_view_name,
                                       urlconf='gbe.urls'),
                'conference_slugs': self.conference_slugs,
                'conference': self.conference}

    def get_rows(self, bids, review_query):
        rows = []
        categories = EvaluationCategory.objects.filter(
            visible=True).order_by('category')
        for bid in bids:
            bid_row = self.set_row_basics(bid, FlexibleEvaluation.objects)
            bid_row['reviews'] = []
            total_average = 0
            valid_categories = 0
            for category in categories:
                average = categories.filter(
                    category=category,
                    flexibleevaluation__bid=bid,
                    flexibleevaluation__ranking__gt=-1
                    ).aggregate(Avg('flexibleevaluation__ranking'))
                if average['flexibleevaluation__ranking__avg']:
                    bid_row['reviews'] += [round(
                        average['flexibleevaluation__ranking__avg'], 2)]
                    total_average += average[
                        'flexibleevaluation__ranking__avg']
                    valid_categories += 1
                else:
                    bid_row['reviews'] += ["--"]
            if valid_categories > 0:
                bid_row['total_average'] = round(
                    total_average/valid_categories, 2)
            else:
                bid_row['total_average'] = "--"
            self.row_hook(bid, bid_row)
            rows.append(bid_row)
        return rows
