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
                prefix="email-select",
                initial={
                    'conference': Conference.objects.all().values_list(
                        'pk',
                        flat=True),
                    'bid_type': initial_bid_choices,
                    'state': [0, 1, 2, 3, 4, 5, 6], })
        self.select_form.fields['bid_type'].choices = self.bid_type_choices

    def get_to_list(self):
        to_list = []
        bid_types = self.select_form.cleaned_data['bid_type']
        query = Q(b_conference__in=self.select_form.cleaned_data['conference'])

        accept_states = self.select_form.cleaned_data['state']
        draft = False
        if "Draft" in self.select_form.cleaned_data['state']:
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
                if bid.profile.user_object.is_active and bidder not in to_list:
                    to_list += [bidder]
            if draft:
                for bid in eval(bid_type).objects.filter(draft_query):
                    bidder = (bid.profile.user_object.email,
                              bid.profile.display_name)
                    if bid.profile.user_object.is_active and (
                            bidder not in to_list):
                        to_list += [bidder]
        return sorted(to_list, key=lambda s: s[1].lower())

    def prep_email_form(self, request):
        to_list = self.get_to_list()
        recipient_info = SecretBidderInfoForm(request.POST,
                                              prefix="email-select")
        recipient_info.fields[
            'bid_type'].choices = self.bid_type_choices
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

        return render(
            request,
            self.template,
            {"selection_form": self.select_form,
             "email_form": email_form,
             "recipient_info": [recipient_info]})
