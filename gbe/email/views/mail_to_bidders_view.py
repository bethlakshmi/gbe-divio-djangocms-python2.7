from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib import messages
from gbe.models import (
    Act,
    Class,
    Conference,
    Costume,
    UserMessage,
    Vendor,
    Volunteer,
)
from gbe.email.forms import (
    SecretBidderInfoForm,
    SelectBidderForm,
)
from gbe.email.views import MailToFilterView
from gbetext import to_list_empty_msg
from django.db.models import Q
from operator import itemgetter


class MailToBiddersView(MailToFilterView):
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Costume Coordinator',
                            'Vendor Coordinator',
                            'Volunteer Coordinator',
                            ]
    template = 'gbe/email/mail_to_bidders.tmpl'
    email_type = 'bid_notifications'

    def groundwork(self, request, args, kwargs):
        self.bid_type_choices = []
        initial_bid_choices = []
        self.url = reverse('mail_to_bidders', urlconf='gbe.email.urls')
        priv_list = self.user.get_email_privs()
        for priv in priv_list:
            self.bid_type_choices += [(priv.title(), priv.title())]
            initial_bid_choices += [priv.title()]
        if 'filter' in request.POST.keys() or 'send' in request.POST.keys():
            self.select_form = SelectBidderForm(
                request.POST,
                prefix="email-select")
        else:
            self.select_form = SelectBidderForm(
                prefix="email-select")
        self.select_form.fields['bid_type'].choices = self.bid_type_choices
        self.select_form.fields['x_bid_type'].choices = self.bid_type_choices

    def get_to_list(self):
        exclude_list = []
        if len(self.select_form.cleaned_data['x_conference']) > 0 or len(
                self.select_form.cleaned_data['x_bid_type']) > 0 or len(
                self.select_form.cleaned_data['x_state']) > 0:
            exclude_list = self.build_any_list(
                self.select_form.cleaned_data['x_conference'],
                self.select_form.cleaned_data['x_bid_type'],
                self.select_form.cleaned_data['x_state'])

        to_list = self.build_any_list(
            self.select_form.cleaned_data['conference'],
            self.select_form.cleaned_data['bid_type'],
            self.select_form.cleaned_data['state'],
            exclude_list)
        return sorted(to_list, key=lambda s: s[1].lower())

    def build_any_list(self,
                       conferences,
                       bid_types,
                       accept_states,
                       exclude_list=[]):
        any_list = []
        query = Q(b_conference__in=conferences)

        draft = False
        if "Draft" in accept_states:
            draft = True
            accept_states.remove('Draft')
            draft_query = query & Q(submitted=False)

        if len(accept_states) > 0:
            query = query & Q(accepted__in=accept_states) & Q(submitted=True)
        elif draft:
            query = draft_query
            draft = False

        for bid_type in bid_types:
            for bid in eval(bid_type).objects.filter(query):
                bidder = (bid.profile.user_object.email,
                          bid.profile.display_name)
                if bid.profile.email_allowed(self.email_type) and (
                        bidder not in exclude_list) and (
                        bidder not in any_list):
                    any_list += [bidder]
            if draft:
                for bid in eval(bid_type).objects.filter(draft_query):
                    bidder = (bid.profile.user_object.email,
                              bid.profile.display_name)
                    if bid.profile.email_allowed(self.email_type) and (
                            bidder not in exclude_list) and (
                            bidder not in any_list):
                        any_list += [bidder]
        return any_list

    def prep_email_form(self, request):
        to_list = self.get_to_list()
        recipient_info = SecretBidderInfoForm(request.POST,
                                              prefix="email-select")
        recipient_info.fields[
            'bid_type'].choices = self.bid_type_choices
        recipient_info.fields[
            'x_bid_type'].choices = self.bid_type_choices
        return to_list, [recipient_info]

    def filter_emails(self, request):
        to_list = self.get_to_list()
        if len(to_list) == 0:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NO_RECIPIENTS",
                defaults={
                    'summary': "Email Sent to Bidders",
                    'description': to_list_empty_msg})
            messages.error(
                request,
                user_message[0].description)
            return render(
                request,
                self.template,
                {"selection_form": self.select_form})
        email_form = self.setup_email_form(request, to_list)
        recipient_info = SecretBidderInfoForm(request.POST,
                                              prefix="email-select")
        recipient_info.fields['bid_type'].choices = self.bid_type_choices
        recipient_info.fields['x_bid_type'].choices = self.bid_type_choices
        return render(
            request,
            self.template,
            {"selection_form": self.select_form,
             "email_form": email_form,
             "recipient_info": [recipient_info],
             "group_filter_note": self.filter_note()},)

    def filter_preferences(self, basic_filter):
        return basic_filter.filter(
            Q(profile__preferences__isnull=True) |
            Q(profile__preferences__send_bid_notifications=True))
