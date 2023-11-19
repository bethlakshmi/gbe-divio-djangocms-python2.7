from django.views.generic import View
from django.urls import reverse
from django.forms import HiddenInput
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from gbe.models import UserMessage
from gbe.email.forms import AdHocEmailForm
from gbetext import (
    send_email_success_msg,
    unsubscribe_text,
)
from django.contrib.sites.models import Site
from post_office import mail
from settings import (
    DEFAULT_FROM_EMAIL,
    DEBUG
)
from gbe.email.functions import create_unsubscribe_link


class MailView(View):

    def setup_email_form(self, request, to_list):
        email_form = AdHocEmailForm(initial={
            'sender': self.user.user_object.email,
            'sender_name': self.user.display_name,
            'to': [c[0] for c in to_list]})
        email_form.fields['to'].choices = to_list
        if not request.user.is_superuser:
            email_form.fields['sender'].widget = HiddenInput()
            email_form.fields['sender_name'].widget = HiddenInput()
        return email_form

    def create_unsubscribe_link(self, email):
        return create_unsubscribe_link(email,
                                       "send_%s" % self.email_type)

    def send_mail(self, request, to_list):
        mail_form = AdHocEmailForm(request.POST)
        mail_form.fields['to'].choices = to_list
        if not request.user.is_superuser:
            mail_form.fields['sender'].widget = HiddenInput()
            mail_form.fields['sender_name'].widget = HiddenInput()
        if mail_form.is_valid():
            email_batch = []
            recipient_string = ""
            if request.user.is_superuser:
                sender = mail_form.cleaned_data['sender']
                sender_name = mail_form.cleaned_data['sender_name']
            else:
                sender = request.user.email
                sender_name = request.user.profile.display_name

            from_complete = "%s <%s>" % (sender_name, DEFAULT_FROM_EMAIL)
            reply_to = "%s <%s>" % (sender_name, sender)
            for email in mail_form.cleaned_data['to']:
                if self.email_type != "individual":
                    footer = unsubscribe_text % (
                        Site.objects.get_current().domain,
                        self.create_unsubscribe_link(email))
                    message = mail_form.cleaned_data['html_message'] + footer
                else:
                    message = mail_form.cleaned_data['html_message']

                # if we're in DEBUG mode, let the sender send to only self
                subject = mail_form.cleaned_data['subject']
                target = email
                if DEBUG:
                    subject = "TO: %s - %s" % (email, subject)
                    target = sender
                email_batch += [{
                    'sender': from_complete,
                    'recipients': [target],
                    'subject': subject,
                    'html_message': message,
                    'headers': {'Reply-to': reply_to}, }]
                if len(recipient_string) > 0:
                    recipient_string = "%s, %s" % (recipient_string, email)
                else:
                    recipient_string = email

            mail.send_many(email_batch)
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SEND_SUCCESS",
                defaults={
                    'summary': "Email Sent to Bidders",
                    'description': send_email_success_msg})
            messages.success(
                request,
                user_message[0].description + recipient_string)
        return mail_form

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MailView, self).dispatch(*args, **kwargs)
