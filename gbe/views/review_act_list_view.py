from django.urls import reverse
from gbe.models import (
    Act,
    ActBidEvaluation,
    EvaluationCategory,
    FlexibleEvaluation,
)
from gbe.views import ReviewBidListView
from django.db.models import Avg


class ReviewActListView(ReviewBidListView):
    page_title = 'Review Acts'
    view_title = 'Act Proposals'
    reviewer_permissions = ('Act Reviewers', )
    object_type = Act
    bid_evaluation_type = ActBidEvaluation
    template = 'gbe/act_bid_review_list.tmpl'
    bid_review_view_name = 'act_review'
    bid_review_list_view_name = 'act_review_list'
    bid_order_fields = ('accepted', 'performer')
    status_index = 3

    def get_context_dict(self):
        context = super(ReviewActListView, self).get_context_dict()
        context.update(
            {'vertical_columns': EvaluationCategory.objects.filter(
                visible=True).order_by('category').values_list(
                'category', flat=True),
             'last_columns': ['Average', 'Action']})
        return context

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
                if average['flexibleevaluation__ranking__avg'] is not None:
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
            rows.append(bid_row)
        return rows
