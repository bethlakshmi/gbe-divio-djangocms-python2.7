from gbe.views import MakeBidView
from django.http import Http404
from django.core.urlresolvers import reverse
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
    default_window_schedule_conflict,
    existing_volunteer_msg,
)
from gbe.views.volunteer_display_functions import (
    validate_interests,
)
from gbe.functions import validate_perms
from gbe.email.functions import (
    notify_reviewers_on_bid_change,
    send_schedule_update_mail,
    send_warnings_to_staff,
)
from settings import DATETIME_FORMAT
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

    def get_reduced_availability(self, the_bid, form):
        '''  Get cases where the volunteer has reduced their availability.
        Either by offering fewer available windows, or by adding to the
        unavailable windows.  Either one is a case for needing to check
        schedule conflict.
        '''
        reduced = []
        for window in the_bid.available_windows.all():
            if window not in form.cleaned_data['available_windows']:
                reduced += [window]

        for window in form.cleaned_data['unavailable_windows']:
            if window not in the_bid.unavailable_windows.all():
                reduced += [window]
        return reduced

    def manage_schedule_problems(self, changed_windows, profile):
        warnings = []
        conflicts = []
        for window in changed_windows:
            conflict_check = get_schedule(
                    profile.user_object,
                    start_time=window.start_time,
                    end_time=window.end_time,
                    labels=[self.bid_object.b_conference.conference_slug])

            # choosing to error silently here, because the function does not
            # have any errors yet, and because this is a public user case
            for conflict in conflict_check.schedule_items:
                if ((conflict.event not in conflicts) and
                        conflict.role == "Volunteer"):
                    conflicts += [conflict.event]
                    warning = {
                        'time': conflict.event.starttime.strftime(
                            DATETIME_FORMAT),
                        'event': str(conflict.event),
                        'interest': conflict.event.eventitem.child(
                            ).volunteer_category_description,
                    }
                    leads = get_all_container_bookings(
                        occurrence_ids=[conflict.event.pk],
                        roles=['Staff Lead', ])
                    for lead in leads.people:
                        warning['lead'] = str(lead.user.profile.badge_name)
                        warning['email'] = lead.user.email
                    for area in StaffArea.objects.filter(
                            conference=self.bid_object.b_conference,
                            slug__in=conflict.event.labels.values_list(
                                'text',
                                flat=True)):
                        warning['lead'] = area.staff_lead.badge_name
                        warning['email'] = area.staff_lead.user_object.email
                    response = remove_booking(
                        occurrence_id=conflict.event.pk,
                        booking_id=conflict.booking_id)
                    warnings += [warning]
        return warnings

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
            self.windows = self.conference.windows()
            self.available_interests = AvailableInterest.objects.filter(
                visible=True).order_by('interest')
        except:
            return self.no_vol_bidding(request)

        if len(self.windows) == 0 or len(self.available_interests) == 0:
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
                instance=self.bid_object,
                available_windows=self.windows,
                unavailable_windows=self.windows)
            self.formset = [
                VolunteerInterestForm(
                    request.POST,
                    instance=interest,
                    initial={'interest': interest.interest},
                    prefix=str(interest.pk)
                ) for interest in self.bid_object.volunteerinterest_set.all()]
        else:
            self.form = the_form(
                request.POST,
                available_windows=self.windows,
                unavailable_windows=self.windows)
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
                instance=self.bid_object,
                available_windows=self.windows,
                unavailable_windows=self.windows)
            for interest in self.bid_object.volunteerinterest_set.all():
                self.formset += [VolunteerInterestForm(
                    instance=interest,
                    initial={'interest': interest.interest},
                    prefix=str(interest.pk))]
        else:
            self.form = VolunteerBidForm(
                initial=self.get_initial(),
                available_windows=self.windows,
                unavailable_windows=self.windows)
            for interest in self.available_interests:
                self.formset += [VolunteerInterestForm(
                    initial={'interest': interest},
                    prefix=str(interest.pk))]
        self.formset += [self.form]
        return render(request,
                      'gbe/bid.tmpl',
                      self.make_context())

    def make_context(self):
        context = super(MakeVolunteerView, self).make_context()
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
                      self.make_context())

    def set_valid_form(self, request):
        if self.bid_edit:
            changed_windows = self.get_reduced_availability(
                self.bid_object,
                self.form)
            warnings = self.manage_schedule_problems(
                changed_windows, self.bid_object.profile)
            if warnings:
                warn_msg = "<br><ul>"
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="AVAILABILITY_CONFLICT",
                    defaults={
                        'summary': "Volunteer Edit Caused Conflict",
                        'description': default_window_schedule_conflict, })
                for warn in warnings:
                    warn_msg += "<li>%s working for %s - as %s" % (
                        warn['time'],
                        warn['event'],
                        warn['interest']
                    )
                    if 'lead' in warn:
                        warn_msg += ", Staff Lead is " + \
                            "<a href='email: %s'>%s</a>" % (
                                warn['email'],
                                warn['lead']
                            )
                    warn_msg += "</li>"
                warn_msg += "</ul>"
                messages.warning(
                    request,
                    user_message[0].description+warn_msg)
                send_schedule_update_mail(
                    self.bid_type,
                    self.bid_object.profile)
                send_warnings_to_staff(
                    self.bid_object.profile,
                    self.bid_type,
                    warnings)

        self.bid_object.b_conference = self.conference
        self.bid_object.profile = self.owner
        self.bid_object.save()

        self.bid_object.available_windows.clear()
        self.bid_object.unavailable_windows.clear()
        for window in self.form.cleaned_data['available_windows']:
            self.bid_object.available_windows.add(window)
        for window in self.form.cleaned_data['unavailable_windows']:
            self.bid_object.unavailable_windows.add(window)
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
