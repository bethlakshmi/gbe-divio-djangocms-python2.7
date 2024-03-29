from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.http import HttpResponseRedirect
from django.urls import reverse
from gbe_logging import log_func
from gbe.models import (
    BidEvaluation,
    UserMessage,
)
from gbe.forms import (
    BidEvaluationForm,
    BidStateChangeForm,
)
from gbe.functions import validate_perms


class ReviewBidView(View):
    bid_state_change_form = BidStateChangeForm
    bid_evaluation_type = BidEvaluation
    bid_evaluation_form_type = BidEvaluationForm
    review_template = 'gbe/bid_review.tmpl'
    performer = None

    def create_action_form(self, bid):
        self.actionform = self.bid_state_change_form(instance=bid)
        self.actionURL = reverse(self.changestate_view_name,
                                 urlconf='gbe.urls',
                                 args=[bid.id])

    def make_context(self):
        return {'readonlyform': self.readonlyform_pieces,
                'reviewer': self.reviewer,
                'form': self.form,
                'actionform': self.actionform,
                'actionURL': self.actionURL,
                'conference': self.b_conference,
                'page_title': self.page_title,
                'view_title': self.view_title,
                'controller_heading': self.controller_heading}

    def bid_review_response(self, request):
        return render(request,
                      self.review_template,
                      self.make_context())

    def create_object_form(self, initial={}):
        initial['first_name'] = self.object.profiles[0].user_object.first_name
        initial['last_name'] = self.object.profiles[0].user_object.last_name
        initial['phone'] = self.object.profiles[0].phone
        self.object_form = self.bid_form_type(instance=self.object,
                                              prefix=self.bid_prefix,
                                              initial=initial)

    def post_response_for_form(self, request):
        if self.form.is_valid():
            evaluation = self.form.save(commit=False)
            evaluation.evaluator = self.reviewer
            evaluation.bid = self.object
            evaluation.save()
            return HttpResponseRedirect("%s?changed_id=%s" % (
                reverse(self.review_list_view_name,
                        urlconf='gbe.urls'),
                self.object.id))
        else:
            return self.bid_review_response(request)

    def object_not_current_redirect(self):
        if self.object.is_current:
            return None
        return HttpResponseRedirect(
            reverse(self.bid_view_name,
                    urlconf='gbe.urls',
                    args=[self.object.id]))

    def get_object(self, request, object_id):
        self.object = get_object_or_404(self.object_type,
                                        id=object_id)

    def set_bid_eval(self):
        self.bid_eval = self.bid_evaluation_type.objects.filter(
            bid_id=self.object.pk,
            evaluator_id=self.reviewer.pk).first()
        if self.bid_eval is None:
            self.bid_eval = self.bid_evaluation_type(
                evaluator=self.reviewer, bid=self.object)

    def groundwork(self, request, args, kwargs):
        object_id = kwargs['object_id']
        self.get_object(request, object_id)
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        if validate_perms(request,
                          self.coordinator_permissions,
                          require=False):
            self.create_action_form(self.object)
        else:
            self.actionform = False
            self.actionURL = False
        self.b_conference = self.object.biddable_ptr.b_conference
        self.set_bid_eval()
        bid_string = self.object.__class__.__name__
        self.page_title = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PAGE_TITLE",
                defaults={
                    'summary': "%s Page Title" % bid_string,
                    'description': 'Review %s' % bid_string
                    })[0].description
        self.view_title = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="FIRST_HEADER",
                defaults={
                    'summary': "%s First Header" % bid_string,
                    'description': '%s Proposal' % bid_string
                    })[0].description
        self.controller_heading = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="CONTROLLER_HEADER",
                defaults={
                    'summary': "%s First Header" % bid_string,
                    'description': "Set %s State" % bid_string
                    })[0].description

    @method_decorator(never_cache, name="get")
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = self.bid_evaluation_form_type(instance=self.bid_eval)
        return (self.object_not_current_redirect() or
                self.bid_review_response(request))

    @method_decorator(never_cache, name="post")
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        self.form = self.bid_evaluation_form_type(request.POST,
                                                  instance=self.bid_eval)
        return (self.object_not_current_redirect() or
                self.post_response_for_form(request))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ReviewBidView, self).dispatch(*args, **kwargs)
