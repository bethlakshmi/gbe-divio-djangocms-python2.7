from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render
from django.db.models import Avg
from gbe.models import (
    Act,
    ActBidEvaluation,
    EvaluationCategory,
    FlexibleEvaluation,
    Profile,
    UserMessage,
)
from gbe.forms import (
    ActBidEvaluationForm,
    FlexibleEvaluationForm,
    BidStateChangeForm,
)
from gbe.functions import validate_perms
from gbe.views.functions import make_show_casting_form
from gbetext import (
    default_act_review_error_msg,
    default_act_review_success_msg,
)
from gbe.views import ReviewBidView
from collections import OrderedDict
from scheduler.idd import get_schedule


class FlexibleReviewBidView(ReviewBidView):
    reviewer_permissions = ('Act Reviewers', )
    review_list_view_name = 'act_review_list'
    coordinator_permissions = ('Act Coordinator', 'Producer')
    bid_state_change_form = BidStateChangeForm
    bid_evaluation_type = FlexibleEvaluation
    bid_evaluation_form_type = FlexibleEvaluationForm
    review_template = 'gbe/flexible_bid_review.tmpl'
    object_type = Act
    changestate_view_name = 'act_changestate'
    bid_view_name = 'act_view'
    review_results = None
    reviewers = None
    notes = None
    readonlyform_pieces = None

    def create_action_form(self, act):
        self.actionform = self.bid_state_change_form(instance=act)
        start = 0
        casting = ""
        for item in get_schedule(
                commitment=act,
                roles=["Performer", "Waitlisted"]).schedule_items:
            if item.event.event_style == "Show":
                start = item.event.pk
                casting = item.commitment.role
        self.actionform = make_show_casting_form(act.b_conference,
                                                 self.actionform,
                                                 start,
                                                 casting)
        self.actionURL = reverse(self.changestate_view_name,
                                 urlconf='gbe.urls',
                                 args=[act.id])
        self.reviewers = Profile.objects.filter(
            flexibleevaluation__bid=act).order_by('display_name').distinct()
        evaluations = FlexibleEvaluation.objects.filter(bid=act)
        self.review_results = OrderedDict()
        for category in self.categories:
            self.review_results[category] = []
            for reviewer in self.reviewers:
                try:
                    self.review_results[category] += [evaluations.get(
                        category=category,
                        evaluator=reviewer,
                        ranking__gt=-1).ranking]
                except:
                    self.review_results[category] += [""]
            try:
                self.review_results[category] += [round(
                    evaluations.filter(
                        category=category,
                        ranking__gt=-1).aggregate(
                        Avg('ranking'))['ranking__avg'], 2)]
            except:
                self.review_results[category] += [""]
        self.notes = ActBidEvaluation.objects.filter(
            bid=act).order_by('evaluator',)

    def bid_review_response(self, request):
        if 'next' in request.GET:
            self.actionURL = "%s?next=%s" % (self.actionURL,
                                             request.GET['next'])
        context = super(FlexibleReviewBidView, self).make_context()
        context.update({
            'act': self.object,
            'performer': self.object.performer,
            'notes_form': self.notes_form,
            'review_results': self.review_results,
            'reviewers': self.reviewers,
            'notes': self.notes,
            'display_contact_info': True,
             })
        return render(
            request,
            self.review_template,
            context)

    def post_response_for_form(self, request):
        valid = True
        for form in self.form:
            valid = valid and form.is_valid()
        if valid and self.notes_form.is_valid():
            for form in self.form:
                form.save()
            self.notes_form.save()
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="REVIEW_SUCCESS",
                defaults={
                    'summary': "Act Review Success",
                    'description': default_act_review_success_msg})
            messages.success(
                request,
                user_message[0].description % (
                    self.object.b_title,
                    str(self.object.performer)))
            return HttpResponseRedirect("%s?changed_id=%s" % (
                reverse(self.review_list_view_name,
                        urlconf='gbe.urls'),
                self.object.id))
        else:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="REVIEW_FORM_ERROR",
                defaults={
                    'summary': "Error Reviewing Act",
                    'description': default_act_review_error_msg})
            messages.error(request, user_message[0].description % (
                self.object.b_title))
            return self.bid_review_response(request)

    def set_bid_eval(self):
        previous_eval = self.bid_evaluation_type.objects.filter(
            bid=self.object,
            evaluator=self.reviewer)
        self.bid_eval_set = []
        for category in self.categories:
            if previous_eval.filter(category=category).exists():
                self.bid_eval_set += [previous_eval.get(category=category)]
            else:
                self.bid_eval_set += [self.bid_evaluation_type(
                    evaluator=self.reviewer,
                    bid=self.object,
                    category=category)]

    def groundwork(self, request, args, kwargs):
        self.categories = EvaluationCategory.objects.filter(
                    visible=True).order_by('category')
        super(FlexibleReviewBidView, self).groundwork(request, args, kwargs)
        self.bid_notes = ActBidEvaluation.objects.filter(
            bid_id=self.object.pk,
            evaluator_id=self.reviewer.pk).first()
        if self.bid_notes is None:
            self.bid_notes = ActBidEvaluation(
                evaluator=self.reviewer, bid=self.object)

    @method_decorator(never_cache, name="get")
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = [FlexibleEvaluationForm(
            instance=bid_eval,
            initial={'category': bid_eval.category},
            prefix=str(bid_eval.category.pk)
            ) for bid_eval in self.bid_eval_set]
        self.notes_form = ActBidEvaluationForm(instance=self.bid_notes)
        return (self.object_not_current_redirect() or
                self.bid_review_response(request))

    @method_decorator(never_cache, name="post")
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = [FlexibleEvaluationForm(
            request.POST,
            instance=bid_eval,
            initial={'category': bid_eval.category},
            prefix=str(bid_eval.category.pk)
            ) for bid_eval in self.bid_eval_set]
        self.notes_form = ActBidEvaluationForm(request.POST,
                                               instance=self.bid_notes)
        return (self.object_not_current_redirect() or
                self.post_response_for_form(request))
