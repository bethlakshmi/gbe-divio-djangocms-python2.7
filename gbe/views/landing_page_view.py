from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from gbe.models import (
    Act,
    Class,
    Costume,
    Profile,
    Vendor,
    Event,
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


@login_required
@log_func
@never_cache
def LandingPageView(request, profile_id=None, historical=False):
    historical = "historical" in list(request.GET.keys())
    standard_context = {}
    standard_context['events_list'] = Event.objects.all()[:5]
    if (profile_id):
        admin_profile = validate_perms(request, ('Registrar',
                                                 'Volunteer Coordinator',
                                                 'Act Coordinator',
                                                 'Class Coordinator',
                                                 'Vendor Coordinator',
                                                 'Ticketing - Admin'))
        viewer_profile = get_object_or_404(Profile, pk=profile_id)
        admin_message = "You are viewing a user's profile, not your own."
    else:
        viewer_profile = validate_profile(request, require=False)
        admin_message = None

    class_to_class_name = {Act: "Act",
                           Class: "Class",
                           Costume: "Costume",
                           Vendor: "Vendor"}
    class_to_view_name = {Act: 'act_review',
                          Class: 'class_review',
                          Costume: 'costume_review',
                          Vendor: 'vendor_review'}

    if viewer_profile:
        bids_to_review = []
        person = Person(
            user=viewer_profile.user_object,
            public_id=viewer_profile.pk,
            public_class="Profile")
        for bid in viewer_profile.bids_to_review():
            bid_type = class_to_class_name.get(bid.__class__, "UNKNOWN")
            view_name = class_to_view_name.get(bid.__class__, None)
            url = ""
            if view_name:
                url = reverse(view_name,
                              urlconf='gbe.urls',
                              args=[str(bid.id)])
            bids_to_review += [{'bid': bid,
                                'url': url,
                                'action': "Review",
                                'bid_type': bid_type}]
        bookings = []
        booking_ids = []
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
            if booking.event.pk not in booking_ids:
                bookings += [booking_item]
                booking_ids += [booking.event.pk]
        current_conf = get_current_conference()
        context = {
            'profile': viewer_profile,
            'historical': historical,
            'alerts': viewer_profile.alerts(historical),
            'standard_context': standard_context,
            'personae': viewer_profile.get_personae(),
            'troupes': viewer_profile.get_troupes(),
            'businesses': viewer_profile.business_set.all(),
            'acts': viewer_profile.get_acts(historical),
            'shows': viewer_profile.get_shows(),
            'classes': viewer_profile.is_teaching(historical),
            'proposed_classes': viewer_profile.proposed_classes(historical),
            'vendors': viewer_profile.vendors(historical),
            'costumes': viewer_profile.get_costumebids(historical),
            'review_items': bids_to_review,
            'tickets': get_purchased_tickets(viewer_profile.user_object),
            'acceptance_states': acceptance_states,
            'admin_message': admin_message,
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
        if not historical:
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
    else:
        context = {'standard_context': standard_context}
    return render(request, 'gbe/landing_page.tmpl', context)
