from django.views.generic.edit import FormMixin
from django.contrib import messages
from gbe.models import UserMessage


class GbeFormMixin(FormMixin):
    # if stay here is true, this should also have the is_popup() mixin or
    # you need to fake that method.  Don't use with Create flows, won't work

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="PAGE_TITLE",
            defaults={
                'summary': "%s Page Title" % self.__class__.__name__,
                'description': self.page_title})[0].description
        context['view_title'] = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="VIEW_TITLE",
            defaults={
                'summary': "%s First Header" % self.__class__.__name__,
                'description': self.view_title})[0].description
        if not hasattr(self, 'intro_text'):
            self.intro_text = ""
        context['intro_text'] = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="INSTRUCTIONS",
            defaults={
                'summary': "%s Instructions" % self.__class__.__name__,
                'description': self.intro_text})[0].description
        if hasattr(self, 'return_url'):
            context['return_url'] = self.return_url
        else:
            context['return_url'] = self.request.GET.get('next',
                                                         self.success_url)
        return context

    def form_valid(self, form, custom_msg=None):
        if hasattr(self, 'valid_message'):
            msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SUCCESS",
                defaults={
                    'summary': "Successful Submission",
                    'description': self.valid_message})[0].description
            if custom_msg is not None:
                msg = msg + custom_msg
            messages.success(self.request, msg)
        return super().form_valid(form)
