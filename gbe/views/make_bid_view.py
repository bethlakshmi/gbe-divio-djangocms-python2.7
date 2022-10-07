from django.views.generic import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.models import (
    Conference,
    UserMessage,
)
from gbe_logging import log_func
from gbe.functions import (
    validate_profile,
)
from gbe.email.functions import notify_reviewers_on_bid_change
from gbetext import (
    no_login_msg,
    fee_instructions,
    full_login_msg,
    payment_needed_msg,
    payment_details_error,
)
from gbe_utils.text import no_profile_msg
from gbe.ticketing_idd_interface import (
    get_payment_details,
    get_ticket_form,
    fee_paid,
)


class MakeBidView(View):
    form = None
    has_draft = True
    instructions = ''
    payment_form = None
    coordinated = False

    def groundwork(self, request, args, kwargs):
        self.owner = validate_profile(request, require=False)
        if not self.owner or not self.owner.complete:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PROFILE_INCOMPLETE",
                defaults={
                    'summary': "Profile Incomplete",
                    'description': no_profile_msg})
            messages.warning(request, user_message[0].description)
            return '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'),
                reverse('%s_create' % self.bid_type.lower(),
                        urlconf='gbe.urls'))
        self.page_title = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PAGE_TITLE",
                defaults={
                    'summary': "%s Page Title" % self.bid_type,
                    'description': self.page_title})[0].description
        self.view_title = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="FIRST_HEADER",
                defaults={
                    'summary': "%s First Header" % self.bid_type,
                    'description': self.view_title})[0].description

        self.bid_object = None
        if "bid_id" in kwargs:
            bid_id = kwargs.get("bid_id")
            self.bid_object = get_object_or_404(self.bid_class, pk=bid_id)
            self.conference = self.bid_object.b_conference
        else:
            self.conference = Conference.objects.filter(
                    accepting_bids=True).first()
        if self.conference is None:
            raise Http404

    def make_post_forms(self, request, the_form):
        if self.bid_object:
            self.form = the_form(
                request.POST,
                instance=self.bid_object,
                initial=self.get_initial(),
                prefix=self.prefix)
        else:
            self.form = the_form(
                request.POST,
                initial=self.get_initial(),
                prefix=self.prefix)
        self.set_up_form()

    def set_up_post(self, request):
        the_form = None
        if 'submit' in list(request.POST.keys()) or not self.has_draft:
            the_form = self.submit_form
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SUBMIT_SUCCESS",
                defaults={
                    'summary': "%s Submit Success" % self.bid_type,
                    'description': self.submit_msg})
        else:
            the_form = self.draft_form
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="DRAFT_SUCCESS",
                defaults={
                    'summary': "%s Save Draft Success" % self.bid_type,
                    'description': self.draft_msg})
        self.make_post_forms(request, the_form)
        return user_message

    def make_context(self, request):
        paid = fee_paid(
            self.bid_type,
            self.owner.user_object.username,
            self.conference)
        instructions = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="BID_INSTRUCTIONS",
            defaults={
                'summary': "%s Bid Instructions" % self.bid_type,
                'description': self.instructions})
        context = {
            'conference': self.conference,
            'forms': [self.form],
            'page_title': self.page_title,
            'view_title': self.view_title,
            'draft_fields': self.draft_fields,
            'submit_fields': self.submit_fields,
            'fee_paid': paid,
            'view_header_text': instructions[0].description,
            }
        if not paid and not self.coordinated:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="FEE_MESSAGE",
                defaults={
                    'summary': "%s Pre-submit Message" % self.bid_type,
                    'description': fee_instructions})

            messages.info(
                request,
                user_message[0].description)
            if self.payment_form:
                context['forms'] += [self.payment_form]
            else:
                context['forms'] += [get_ticket_form(self.bid_class.__name__,
                                                     self.conference)]
        return context

    def get_create_form(self, request):
        if self.bid_object:
            self.form = self.submit_form(
                prefix=self.prefix,
                instance=self.bid_object,
                initial=self.get_initial())
        else:
            self.form = self.submit_form(
                prefix=self.prefix,
                initial=self.get_initial())
        self.set_up_form()

        return render(
            request,
            'gbe/bid.tmpl',
            self.make_context(request)
        )

    def check_validity(self, request):
        return self.form.is_valid()

    def set_up_form(self):
        pass

    def get_invalid_response(self, request):
        self.set_up_form()
        context = self.make_context(request)
        return render(
            request,
            'gbe/bid.tmpl',
            context)

    def submit_bid(self, request):
        self.bid_object.submitted = True
        self.bid_object.save()
        notify_reviewers_on_bid_change(
            self.owner,
            self.bid_object,
            self.bid_type,
            "Submission",
            self.conference,
            '%s Reviewers' % self.bid_type,
            reverse('%s_review' % self.bid_type.lower(),
                    urlconf='gbe.urls'))

    @never_cache
    @log_func
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            follow_on = '?next=%s' % reverse(
                '%s_create' % self.bid_type.lower(),
                urlconf='gbe.urls')
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="USER_NOT_LOGGED_IN",
                defaults={
                    'summary': "Need Login - %s Bid",
                    'description': no_login_msg})
            full_msg = full_login_msg % (
                user_message[0].description,
                reverse('login', urlconf='gbe.urls') + follow_on)
            messages.warning(request, full_msg)

            return HttpResponseRedirect(
                reverse('register', urlconf='gbe.urls') + follow_on)

        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return HttpResponseRedirect(redirect)

        return self.get_create_form(request)

    @never_cache
    @log_func
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        cart_items = []
        paypal_button = None
        total = None
        redirect = None
        redirect = self.groundwork(request, args, kwargs)
        if redirect:
            return HttpResponseRedirect(redirect)

        user_message = self.set_up_post(request)

        # check bid validity
        if not self.check_validity(request):
            return self.get_invalid_response(request)

        if not self.coordinated and not fee_paid(
                self.bid_type,
                self.owner.user_object.username,
                self.conference) and "draft" not in list(request.POST.keys()):
            self.payment_form = get_ticket_form(self.bid_class.__name__,
                                                self.conference,
                                                request.POST)
            if not self.payment_form.is_valid():
                error_message = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code="PAYMENT_CHOICE_INVALID",
                        defaults={
                            'summary': "User Made Invalid Ticket Choice",
                            'description': payment_details_error})
                messages.error(request, error_message[0].description)
                return self.get_invalid_response(request)

        # save bid
        if not self.bid_object:
            self.bid_object = self.form.save(commit=False)

        self.set_valid_form(request)
        if 'phone' in self.form.cleaned_data:
            self.owner.phone = self.form.cleaned_data['phone']
            self.owner.save()
        if 'first_name' in self.form.cleaned_data:
            self.owner.user_object.first_name = \
                self.form.cleaned_data['first_name']
        if 'last_name' in self.form.cleaned_data:
            self.owner.user_object.last_name = \
                self.form.cleaned_data['last_name']
        self.owner.user_object.save()

        # if this isn't a draft, move forward through process, setting up
        # payment review if payment is needed
        if "submit" in list(request.POST.keys()):
            if self.payment_form:
                cart_items, paypal_button, total = get_payment_details(
                    request,
                    self.payment_form,
                    self.bid_type,
                    self.bid_object.pk,
                    self.owner.user_object.pk)

                dynamic_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="NOT_PAID_INSTRUCTIONS",
                    defaults={
                        'summary': "%s Not Paid" % self.bid_type,
                        'description': payment_needed_msg})
                page_title = '%s Payment' % self.bid_type
                return render(
                    request,
                    'gbe/confirm_pay.tmpl',
                    {'dynamic_message': dynamic_message[0].description,
                     'page_title': page_title,
                     'cart_items': cart_items,
                     'total': total,
                     'paypal_button': paypal_button})
            else:
                redirect = self.submit_bid(request)

        messages.success(request, user_message[0].description)
        return HttpResponseRedirect(
            redirect or reverse('home', urlconf='gbe.urls'))

    def dispatch(self, *args, **kwargs):
        return super(MakeBidView, self).dispatch(*args, **kwargs)
