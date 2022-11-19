from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from django.views.generic import View
from django.db.models import Q
from gbe.models import (
    Act,
    Class,
    Costume,
    Profile,
    Vendor,
    UserMessage,
)
from gbe.ticketing_idd_interface import (
    get_purchased_tickets,
    verify_performer_app_paid,
    verify_vendor_app_paid,
)
from gbetext import (
    acceptance_states,
    current_bid_msg,
    historic_bid_msg,
    interested_explain_msg,
)
from gbe.functions import (
    get_current_conference,
    validate_perms,
    validate_profile,
)
from gbe_logging import log_func
from scheduler.idd import (
    get_bookings,
    get_eval_info,
    get_schedule,
)
from scheduler.data_transfer import Person
from gbe_utils.mixins import ProfileRequiredMixin


class LandingPageView(ProfileRequiredMixin, View):

    def groundwork(self, request, args, kwargs):
        self.historical = "historical" in list(request.GET.keys())
        self.is_staff_lead = False
        self.admin_message = None

        if "profile_id" in kwargs:
            profile_id = kwargs.get("profile_id")
            self.admin_profile = validate_perms(request,
                                                ('Registrar',
                                                 'Volunteer Coordinator',
                                                 'Act Coordinator',
                                                 'Class Coordinator',
                                                 'Vendor Coordinator',
                                                 'Ticketing - Admin'))
            self.viewer_profile = get_object_or_404(Profile, pk=profile_id)
            self.admin_message = "You are viewing a user's profile, " + \
                "not your own."
        else:
            self.viewer_profile = validate_profile(request, require=False)
        self.is_staff_lead = validate_perms(request,
                                            ['Staff Lead', ],
                                            require=False)

    def dispatch(self, *args, **kwargs):
        return super(LandingPageView, self).dispatch(*args, **kwargs)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        viewer_profile = self.viewer_profile
        context = {}
        bids_to_review = []

        person = Person(
            user=viewer_profile.user_object,
            public_id=viewer_profile.pk,
            public_class="Profile")
        for bid in viewer_profile.bids_to_review():
            bids_to_review += [{
                'bid': bid,
                'url': reverse('%s_review' % bid.__class__.__name__.lower(),
                               urlconf='gbe.urls',
                               args=[str(bid.id)]),
                'action': "Review",
                'bid_type': bid.__class__.__name__}]
        personae, troupes = viewer_profile.get_performers(organize=True)
        bookings = []
        booking_ids = []
        manage_shows = []
        shows = []
        classes = []
        acts = Act.objects.filter(
            Q(performer__in=personae) | Q(performer__in=troupes))

        for booking in get_schedule(
                viewer_profile.user_object).schedule_items:
            gbe_event = booking.event.eventitem.child()
            booking_item = {
                'id': booking.event.pk,
                'role':  booking.role,
                'conference': gbe_event.e_conference,
                'starttime': booking.event.starttime,
                'interested': get_bookings(
                    [booking.event.pk],
                    roles=["Interested"]).people,
                'eventitem_id': gbe_event.eventitem_id,
                'title': gbe_event.e_title, }
            if gbe_event.calendar_type == "Conference" and (
                    booking.role not in ("Teacher", "Performer", "Moderator")):
                eval_check = get_eval_info(booking.event.pk, person)
                if len(eval_check.questions) > 0:
                    if len(eval_check.answers) > 0:
                        booking_item['evaluate'] = "disabled"
                    else:
                        booking_item['evaluate'] = reverse(
                            'eval_event',
                            args=[booking.event.pk, ],
                            urlconf='gbe.scheduling.urls')
            elif gbe_event.calendar_type == "Conference":
                classes += [booking_item]
            if gbe_event.e_conference.status != "completed":
                if gbe_event.calendar_type == "General" and (
                        booking.commitment is not None):
                    shows += [(gbe_event,
                               acts.get(id=booking.commitment.class_id))]

                # roles assigned direct to shows
                if booking.role in (
                        'Stage Manager',
                        'Technical Director',
                        'Producer'):
                    manage_shows += [booking.event]
                # staff leads often work a volunteer slot in the show
                elif self.is_staff_lead and booking.event.parent is not None:
                    parent = booking.event.parent
                    if parent not in manage_shows and (
                            parent.event_style == "Show"):
                        manage_shows += [parent]
            if booking.event.pk not in booking_ids:
                bookings += [booking_item]
                booking_ids += [booking.event.pk]
        current_conf = get_current_conference()
        # filter for conf AFTER bookings
        if self.historical:
            acts = acts.filter(b_conference__status="completed")
        else:
            acts = acts.exclude(b_conference__status="completed")
        context = {
            'profile': viewer_profile,
            'historical': self.historical,
            'alerts': viewer_profile.alerts(shows, classes),
            'personae': personae,
            'troupes': troupes,
            'manage_shows': manage_shows,
            'businesses': viewer_profile.business_set.all(),
            'acts': acts,
            'shows': shows,
            'proposed_classes': viewer_profile.proposed_classes(
                self.historical),
            'vendors': viewer_profile.vendors(self.historical),
            'costumes': viewer_profile.get_costumebids(self.historical),
            'review_items': bids_to_review,
            'tickets': get_purchased_tickets(viewer_profile.user_object),
            'acceptance_states': acceptance_states,
            'admin_message': self.admin_message,
            'bookings': bookings,
            'act_paid': verify_performer_app_paid(
                viewer_profile.user_object.username,
                current_conf),
            'vendor_paid': verify_vendor_app_paid(
                viewer_profile.user_object.username,
                current_conf),
            'logged_in_message': UserMessage.objects.get_or_create(
                view="LandingPageView",
                code="GENERAL_MESSAGE",
                defaults={
                    'summary': "Left hand sidebar message",
                    'description': ''})[0].description
            }
        if not self.historical:
            user_message = UserMessage.objects.get_or_create(
                view="LandingPageView",
                code="ABOUT_INTERESTED",
                defaults={
                    'summary': "About Interested Attendees",
                    'description': interested_explain_msg})
            right_side_msg = UserMessage.objects.get_or_create(
                view="LandingPageView",
                code="CURRENT_BID_INSTRUCTION",
                defaults={
                    'summary': "Right Hand Sidebar - Current Bid Message",
                    'description': current_bid_msg})
            context['interested_info'] = user_message[0].description
        else:
            right_side_msg = UserMessage.objects.get_or_create(
                view="LandingPageView",
                code="HISTORICAL_BID_INSTRUCTION",
                defaults={
                    'summary': "Right Hand Sidebar - Historical Bid Message",
                    'description': historic_bid_msg})
        context['right_side_intro'] = right_side_msg[0].description
        return render(request, 'gbe/landing_page.tmpl', context)
