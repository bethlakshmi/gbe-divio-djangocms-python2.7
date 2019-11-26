from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.conf import settings
from django.core.urlresolvers import reverse
from post_office.models import EmailTemplate
from django.contrib import messages
from gbe.models import (
    EmailTemplateSender,
    UserMessage,
)
from gbetext import (
    save_email_template_success_msg,
    unsub_footer_include,
    unsub_footer_plain_include,
)
from gbe.email.forms import EmailTemplateForm
from gbe.email.functions import (
    get_mail_content,
    get_user_email_templates,
)
from gbe_logging import log_func
from gbe.functions import validate_perms


class EditTemplateView(View):
    page_title = 'Edit Email Template'
    view_title = 'Edit Email Template'
    submit_button = 'Save Template'
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Costume Coordinator',
                            'Scheduling Mavens',
                            'Vendor Coordinator',
                            'Volunteer Coordinator',
                            ]

    def groundwork(self, request, args, kwargs):
        self.user = validate_perms(request, self.reviewer_permissions)

        self.template = None
        if "template_name" in kwargs:
            template_name = kwargs.get("template_name")
            # permission and syntax check
            match_template_info = None
            for template in get_user_email_templates(self.user):
                if template_name == template['name']:
                    match_template_info = template
            if not match_template_info:
                raise Http404
            try:
                self.template = EmailTemplate.objects.get(
                    name=template_name)
            except:
                textcontent, htmlcontent = get_mail_content(
                    match_template_info['default_base'])
                self.initial = {
                    'name': template_name,
                    'subject': match_template_info['default_subject'],
                    'html_content': htmlcontent,
                    'description': match_template_info['description'],
                    'sender': settings.DEFAULT_FROM_EMAIL}

    def make_context(self):
        context = {
            'forms': [self.form],
            'nodraft': self.submit_button,
            'page_title': self.page_title,
            'view_title': self.view_title}
        if self.template:
            context['description'] = self.template.description
            context['name'] = self.template.name
        else:
            context['description'] = self.initial['description']
            context['name'] = self.initial['name']
        return context

    def get_edit_template_form(self, request):
        if self.template:
            sender = None
            if EmailTemplateSender.objects.filter(
                    template=self.template).exists():
                sender = self.template.sender.from_email
            else:
                sender = settings.DEFAULT_FROM_EMAIL

            self.form = EmailTemplateForm(
                instance=self.template,
                initial={'sender': sender})
        else:
            self.form = EmailTemplateForm(
                initial=self.initial)
        return render(
            request,
            'gbe/email/edit_email_template.tmpl',
            self.make_context()
        )

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return self.get_edit_template_form(request)

    @never_cache
    @log_func
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)

        if self.template:
            self.form = EmailTemplateForm(
                request.POST,
                instance=self.template)
        else:
            self.form = EmailTemplateForm(
                request.POST)

        if not self.form.is_valid():
            return render(request,
                          'gbe/email/edit_email_template.tmpl',
                          self.make_context())
        else:
            # special handling for unsubscribe, so users can't hack it
            if self.template.name in ("daily schedule", 
                                      "volunteer schedule update"):
                self.template = self.form.save(commit=False)
                if unsub_footer_include not in self.template.html_content:
                    self.template.html_content = self.template.html_content + \
                        unsub_footer_include
                    self.template.content = self.template.content + \
                        unsub_footer_plain_include
                elif unsub_footer_include in self.template.content:
                    self.template.content = self.template.content.replace(
                        unsub_footer_include,
                        unsub_footer_plain_include)
                self.template.save()
            else:
                self.template = self.form.save()
            if EmailTemplateSender.objects.filter(
                    template=self.template).exists():
                self.template.sender.from_email = self.form.cleaned_data[
                    'sender']
            else:
                self.template.sender = EmailTemplateSender(
                    template=self.template,
                    from_email=self.form.cleaned_data['sender'])
            self.template.sender.save()

        user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SAVE_SUCCESS",
                defaults={
                    'summary': "Email Template Success",
                    'description': save_email_template_success_msg})
        messages.success(request,
                         user_message[0].description + self.template.name)
        return HttpResponseRedirect(
            reverse('list_template', urlconf='gbe.email.urls'))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditTemplateView, self).dispatch(*args, **kwargs)
