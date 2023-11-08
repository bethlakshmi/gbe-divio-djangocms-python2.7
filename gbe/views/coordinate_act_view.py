from gbe.views import MakeActView
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.contrib.auth.mixins import PermissionRequiredMixin
from gbe.models import TechInfo
from gbe.forms import ActCoordinationForm
from gbetext import (
    act_coord_instruct,
    missing_profile_info,
    no_comp_msg,
)
from gbe.email.functions import send_bid_state_change_mail
from gbe.ticketing_idd_interface import comp_act
from gbe.models import UserMessage
from django.contrib import messages


class CoordinateActView(PermissionRequiredMixin, MakeActView):
    page_title = 'Create Act for Coordinator'
    view_title = 'Book an Act'
    has_draft = True
    permission_required = 'gbe.assign_act'
    submit_form = ActCoordinationForm
    draft_form = ActCoordinationForm
    coordinated = True
    instructions = act_coord_instruct
    normal_redirect = reverse_lazy('act_review_list', urlconf='gbe.urls')

    def groundwork(self, request, args, kwargs):
        # do the basic bid stuff, but NOT the regular act stuff
        return super(MakeActView, self).groundwork(request, args, kwargs)

    def get_initial(self):
        return {'b_conference': self.conference}

    def set_valid_form(self, request):
        techinfo = TechInfo(
            duration=self.form.cleaned_data['act_duration'],
            track_title=self.form.cleaned_data['track_title'],
            track_artist=self.form.cleaned_data['track_artist']
            )
        techinfo.save()
        self.bid_object.tech = techinfo
        self.bid_object.save()
        self.form.save()
        check = comp_act(self.bid_object.performer.contact.user_object,
                         self.conference)
        if not check:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NO_COMP_MADE",
                defaults={
                    'summary': "No Act Submit Ticket, No Comp for User",
                    'description': no_comp_msg})
            messages.error(request, user_message[0].description)

    def make_context(self, request):
        context = super(MakeActView, self).make_context(request)
        context['submit_button'] = "Submit & Review"
        return context

    def submit_bid(self, request):
        self.bid_object.submitted = True
        self.bid_object.save()
        send_bid_state_change_mail(
            str(self.bid_class.__name__).lower(),
            self.bid_object.profile.contact_email,
            self.bid_object.profile.get_badge_name(),
            self.bid_object,
            self.bid_object.accepted)

        redirect = reverse('act_review',
                           urlconf="gbe.urls",
                           args=[self.bid_object.id])

        if not self.bid_object.performer.contact.participation_ready:
            redirect = "%s?next=%s" % (
                reverse('admin_profile',
                        urlconf="gbe.urls",
                        args=[self.bid_object.performer.contact.pk]),
                redirect)
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="MISSING_PROFILE_INFO",
                defaults={
                    'summary': "No First, Last, Phone",
                    'description': missing_profile_info})
            messages.warning(request, user_message[0].description)

        elif 'next' in request.GET:
            redirect = "%s?next=%s" % (redirect, request.GET['next'])

        return redirect

    def get_invalid_response(self, request):
        # Make Act gives personalized links, they are irrelevant here.
        return super(MakeActView, self).get_invalid_response(request)
