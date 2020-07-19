from gbe.views import MakeBidView
from django.http import Http404
from django.urls import reverse
from django.shortcuts import render
from django.contrib import messages
from django.forms import ModelChoiceField
from gbe.forms import (
    VolunteerBidForm,
    VolunteerInterestForm,
)
from gbe.models import (
    AvailableInterest,
    StaffArea,
    UserMessage,
    Volunteer,
)
from gbetext import (
    default_volunteer_edit_msg,
    default_volunteer_submit_msg,
    default_volunteer_no_interest_msg,
    default_volunteer_no_bid_msg,
    existing_volunteer_msg,
)
from gbe.views.volunteer_display_functions import (
    validate_interests,
)
from gbe.functions import validate_perms
from gbe.email.functions import notify_reviewers_on_bid_change
from settings import GBE_DATETIME_FORMAT
from scheduler.idd import (
    get_all_container_bookings,
    get_schedule,
    remove_booking,
)


class MakeVolunteerView(MakeBidView):
    page_title = "Volunteer"
    view_title = "Volunteer at the Expo"
    draft_fields = ['b_title', 'creator']
    submit_fields = [
        'b_title',
        'creator',
        'active_use',
        'pieces',
        'b_description',
        'pasties',
        'dress_size',
        'picture']
    bid_type = "Volunteer"
    has_draft = False
    submit_msg = default_volunteer_submit_msg
    draft_msg = None
    submit_form = VolunteerBidForm
    draft_form = None
    prefix = None
    bid_class = Volunteer
    bid_edit = False
    coordinator = None
    action = "Update"

    def no_vol_bidding(self, request):
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="NO_BIDDING_ALLOWED",
            defaults={
                'summary': "Volunteer Bidding Blocked",
                'description': default_volunteer_no_bid_msg})
        messages.error(request, user_message[0].description)
        return reverse('home', urlconf='gbe.urls')

    def groundwork(self, request, args, kwargs):
        redirect = super(
            MakeVolunteerView,
            self).groundwork(request, args, kwargs)
        if redirect:
            return redirect

        if self.bid_object and (self.bid_object.profile != self.owner):
            self.coordinator = validate_perms(
                request,
                ('Volunteer Coordinator',))
            self.owner = self.bid_object.profile

        try:
            self.available_interests = AvailableInterest.objects.filter(
                visible=True).order_by('interest')
        except:
            return self.no_vol_bidding(request)

        if not self.bid_object:
            self.action = "Submission"
            try:
                existing_bid = self.owner.volunteering.get(
                    b_conference=self.conference)
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="FOUND_EXISTING_BID",
                    defaults={
                        'summary': "Existing Volunteer Offer Found",
                        'description': existing_volunteer_msg})
                messages.success(request, user_message[0].description)
                return reverse(
                    'volunteer_edit',
                    urlconf='gbe.urls',
                    args=[existing_bid.id])
            except:
                pass

    def get_initial(self):
        title = 'volunteer bid: %s' % self.owner.display_name
        initial = {}
        if not self.bid_object:
            initial = {
                'profile': self.owner,
                'b_title': title,
                'description': 'volunteer bid',
                'submitted': True}
        return initial

    def make_post_forms(self, request, the_form):
        if self.bid_object:
            self.form = the_form(
                request.POST,
                instance=self.bid_object)
            self.formset = [
                VolunteerInterestForm(
                    request.POST,
                    instance=interest,
                    initial={'interest': interest.interest},
                    prefix=str(interest.pk)
                ) for interest in self.bid_object.volunteerinterest_set.all()]
        else:
            self.form = the_form(
                request.POST)
            self.formset = [
                VolunteerInterestForm(
                    request.POST,
                    initial={'interest': interest},
                    prefix=str(interest.pk)
                    ) for interest in self.available_interests]

    def set_up_post(self, request):
        user_message = super(MakeVolunteerView, self).set_up_post(request)
        if self.bid_object:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="EDIT_SUCCESS",
                defaults={
                    'summary': "Volunteer Edit Success",
                    'description': default_volunteer_edit_msg})
        return user_message

    def get_create_form(self, request):
        self.formset = []
        if self.bid_object:
            self.form = VolunteerBidForm(
                instance=self.bid_object)
            for interest in self.bid_object.volunteerinterest_set.all():
                self.formset += [VolunteerInterestForm(
                    instance=interest,
                    initial={'interest': interest.interest},
                    prefix=str(interest.pk))]
        else:
            self.form = VolunteerBidForm(
                initial=self.get_initial())
            for interest in self.available_interests:
                self.formset += [VolunteerInterestForm(
                    initial={'interest': interest},
                    prefix=str(interest.pk))]
        self.formset += [self.form]
        return render(request,
                      'gbe/bid.tmpl',
                      self.make_context(request))

    def make_context(self, request):
        context = super(MakeVolunteerView, self).make_context(request)
        context['forms'] = self.formset
        context['nodraft'] = 'Submit'
        return context

    def check_validity(self, request):
        self.valid_interests, self.like_one_thing = validate_interests(
            self.formset)
        if self.bid_object:
            self.bid_edit = True
        return self.form.is_valid() and \
            self.valid_interests and self.like_one_thing

    def get_invalid_response(self, request):
        self.formset += [self.form]
        if not self.like_one_thing:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NO_INTERESTS_SUBMITTED",
                defaults={
                    'summary': "Volunteer Has No Interests",
                    'description': default_volunteer_no_interest_msg})
            messages.error(request, user_message[0].description)

        return render(request,
                      'gbe/bid.tmpl',
                      self.make_context(request))

    def set_valid_form(self, request):
        self.bid_object.b_conference = self.conference
        self.bid_object.profile = self.owner
        self.bid_object.save()

        for interest_form in self.formset:
            vol_interest = interest_form.save(commit=False)
            vol_interest.volunteer = self.bid_object
            vol_interest.save()

    def submit_bid(self, request):
        self.bid_object.submitted = True
        self.bid_object.save()
        bid_review_url = reverse(
            '%s_review' % self.bid_type.lower(),
            urlconf='gbe.urls')

        if not self.coordinator:
            notify_reviewers_on_bid_change(
                self.owner,
                self.bid_object,
                self.bid_type,
                self.action,
                self.conference,
                '%s Reviewers' % self.bid_type,
                bid_review_url)
        else:
            return bid_review_url
