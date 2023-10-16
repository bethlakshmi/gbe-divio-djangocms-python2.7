from django.urls import reverse
from gbe.forms import ActFilterForm
from gbe.models import (
    Act,
    ActBidEvaluation,
    EvaluationCategory,
    FlexibleEvaluation,
    Profile,
    UserMessage,
)
from gbe.views import ReviewBidListView
from django.db.models import Avg, Count
from django.contrib import messages
from gbetext import (
    acceptance_states,
    apply_filter_msg,
    clear_filter_msg,
    no_filter_msg,
)
from django.db.models import Q


class ReviewActListView(ReviewBidListView):
    reviewer_permissions = ('Act Reviewers', )
    object_type = Act
    bid_evaluation_type = ActBidEvaluation
    template = 'gbe/act_bid_review_list.tmpl'
    bid_review_view_name = 'act_review'
    bid_review_list_view_name = 'act_review_list'
    bid_order_fields = ('accepted', 'bio')
    status_index = 3
    filter_form = None

    def get_bids(self, request=None):
        if request and 'filter' in list(request.POST.keys()):
            self.filter_form = ActFilterForm(request.POST)
            if self.filter_form.is_valid() and len(
                    self.filter_form.cleaned_data['shows_preferences']) > 0:
                query = Q(shows_preferences__exact='')
                for choice in self.filter_form.cleaned_data[
                        'shows_preferences']:
                    query = query | Q(shows_preferences__contains=choice)
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="FILTER_APPLIED",
                    defaults={
                        'summary': "Results have been filtered",
                        'description': apply_filter_msg})
                messages.success(request, user_message[0].description)
                return self.object_type.objects.filter(
                    query,
                    submitted=True,
                    b_conference=self.conference,
                    ).order_by(*self.bid_order_fields)
            elif not self.filter_form.is_valid():
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="FILTER_FORM_ERROR",
                    defaults={
                        'summary': "Problem with Filter",
                        'description': no_filter_msg})
                messages.warning(request, user_message[0].description)
            else:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="FILTER_CLEARED",
                    defaults={
                        'summary': "No choices in Filter",
                        'description': clear_filter_msg})
                messages.success(request, user_message[0].description)

        return self.object_type.objects.filter(
            submitted=True,
            b_conference=self.conference).order_by(*self.bid_order_fields)

    def get_context_dict(self):
        context = super(ReviewActListView, self).get_context_dict()
        accept_metrics = {}
        no_decision_count = 0
        for accept_state in self.object_type.objects.filter(
                b_conference=self.conference,
                submitted=True).values('accepted').annotate(count=
                Count("id")).order_by():
            accept_metrics[acceptance_states[
                accept_state['accepted']][1]] = accept_state['count']
            if accept_state['accepted'] == 0:
                no_decision_count = accept_state['count']

        context.update(
            {'vertical_columns': EvaluationCategory.objects.filter(
                visible=True).order_by('category').values_list(
                'category', flat=True),
             'last_columns': ['Average', 'Action'],
             'review_metrics':  {
                'total_by_status': accept_metrics,
                'total_by_reviewer': self.object_type.objects.filter(
                    b_conference=self.conference,
                    submitted=True,
                    accepted=0).values(
                    'actbidevaluation__evaluator__display_name'
                    ).annotate(count=Count("id")).order_by(),
                'total_no_decision': no_decision_count,
                'act_reviewers': Profile.objects.filter(
                    user_object__groups__name__in=self.reviewer_permissions)
            }})

        if self.conference.status in ('upcoming', 'ongoing'):
            if self.filter_form is not None:
                context['filter_form'] = self.filter_form
            else:
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
