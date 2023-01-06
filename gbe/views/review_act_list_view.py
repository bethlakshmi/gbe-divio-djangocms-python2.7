from django.urls import reverse
from gbe.forms import ActFilterForm
from gbe.models import (
    Act,
    ActBidEvaluation,
    EvaluationCategory,
    FlexibleEvaluation,
    UserMessage,
)
from gbe.views import ReviewBidListView
from django.db.models import Avg
from django.contrib import messages
from gbetext import no_filter_msg


class ReviewActListView(ReviewBidListView):
    reviewer_permissions = ('Act Reviewers', )
    object_type = Act
    bid_evaluation_type = ActBidEvaluation
    template = 'gbe/act_bid_review_list.tmpl'
    bid_review_view_name = 'act_review'
    bid_review_list_view_name = 'act_review_list'
    bid_order_fields = ('accepted', 'performer')
    status_index = 3

    def get_bids(self, request=None):
        if request and 'filter' in list(request.POST.keys()):
            form = ActFilterForm(request.POST)
            if form.is_valid():
                return self.object_type.objects.filter(
                    submitted=True,
                    b_conference=self.conference,
                    shows_preferences__in=form.cleaned_data[shows_preferences]
                    ).order_by(*self.bid_order_fields)
            else:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="FILTER_FORM_ERROR",
                    defaults={
                        'summary': "Problem with Filter",
                        'description': no_filter_msg})
                messages.warning(request, user_message[0].description)
        return self.object_type.objects.filter(
            submitted=True,
            b_conference=self.conference).order_by(*self.bid_order_fields)

    def get_context_dict(self):
        context = super(ReviewActListView, self).get_context_dict()
        context.update(
            {'vertical_columns': EvaluationCategory.objects.filter(
                visible=True).order_by('category').values_list(
                'category', flat=True),
             'last_columns': ['Average', 'Action']})

        if self.conference.status in ('upcoming', 'ongoing'):
            context['filter_form'] = ActFilterForm
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
