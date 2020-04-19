from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from gbe.models import UserMessage
from gbe.email.views import MailView
from gbetext import (
    group_filter_note,
    unknown_request,
)
from gbe.functions import validate_perms
from django.contrib.auth.models import User


class MailToFilterView(MailView):
    '''
        This is the parent for any class that is providing an email filter
        The class should provide:
            - the template for display (extending mail_to_group.tmpl)
            - the url that represents this flow
            - groundwork(self, request, args, kwargs) - to set the select_form
            - prep_email_form(request) - returns to_list, list of recipient
                info forms for preparing the email recipient list
            - filter_emails(request) - set up the filter form, when there is an
              error
            - filter_preferences(query) - filter for users who have opted out
              of being contacted by this filter.  Should take a User filter.
            - get_select_forms - to provide forms and other details around
              making a selection.
    '''
    def get_everyone(self, request):
        to_list = []
        if not request.user.is_superuser:
            return to_list
        filter_everyone = self.filter_preferences(
            User.objects.filter(is_active=True).exclude(
                username="limbo"))
        for user_object in filter_everyone.order_by('email'):
            if hasattr(user_object, 'profile') and len(
                    user_object.profile.display_name) > 0:
                to_list += [(user_object.email,
                             user_object.profile.display_name)]
            else:
                to_list += [(user_object.email, user_object.username)]
        return to_list

    def filter_everyone(self, request):
        to_list = self.get_everyone(request)
        if len(to_list) == 0:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="UNKNOWN_ACTION",
                defaults={
                    'summary': "Unknown Request",
                    'description': unknown_request})
            messages.error(
                request,
                user_message[0].description)
            return render(
                request,
                'gbe/email/mail_to_bidders.tmpl',
                {"selection_form": self.select_form})
        email_form = self.setup_email_form(request, to_list)
        return render(
            request,
            'gbe/email/mail_to_bidders.tmpl',
            {"selection_form": self.select_form,
             "email_form": email_form,
             "everyone": True,
             "group_filter_note": self.filter_note()})

    def filter_note(self):
        user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="GROUP_FILTER_INFO",
                defaults={
                    'summary': "Help for the user of any group email feature",
                    'description': group_filter_note})
        return user_message[0].description

    def select_form_is_valid(self):
        return self.select_form.is_valid()

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.user = validate_perms(request, self.reviewer_permissions)
        self.groundwork(request, args, kwargs)
        return render(
            request,
            self.template,
            self.get_select_forms())

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.user = validate_perms(request, self.reviewer_permissions)
        self.groundwork(request, args, kwargs)
        if 'send' in list(request.POST.keys()):
            everyone = False
            recipient_info = None
            to_list = []
            if 'everyone' in list(request.POST.keys()):
                to_list = self.get_everyone(request)
                everyone = True
            elif self.select_form_is_valid():
                to_list, recipient_info = self.prep_email_form(request)
            if len(to_list) > 0:
                mail_form = self.send_mail(request, to_list)
                if mail_form.is_valid():
                    return HttpResponseRedirect(self.url)
                else:
                    context = {
                        "email_form": mail_form,
                        "recipient_info": [recipient_info],
                        "everyone": everyone}
                    context.update(self.get_select_forms())
                    return render(
                        request,
                        self.template,
                        context)
        elif 'everyone' in list(request.POST.keys()):
            return self.filter_everyone(request)
        elif ('filter' in list(request.POST.keys()) or 'refine' in list(request.POST.keys(
                ))) and self.select_form_is_valid():
            return self.filter_emails(request)

        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="UNKNOWN_ACTION",
            defaults={
                'summary': "Unknown Request",
                'description': unknown_request})
        messages.error(
                request,
                user_message[0].description)
        return render(
            request,
            self.template,
            self.get_select_forms())
