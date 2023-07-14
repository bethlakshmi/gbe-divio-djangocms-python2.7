from django.views.generic.edit import ModelFormMixin
from django.contrib import messages
from gbe.models import UserMessage


class GbeFormMixin(ModelFormMixin):
    # if stay here is true, this should also have the is_popup() mixin or
    # you need to fake that method.  Don't use with Create flows, won't work
    stay_here = False

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
        context['return_url'] = self.request.GET.get('next', self.success_url)

        # this is all unique to performer registration
        if hasattr(self, 'mode'):
            context['mode'] = self.mode
            if hasattr(self, 'no_tabs'):
                context['no_tabs'] = self.no_tabs
            else:
                context['include_troupe'] = int(
                    self.kwargs.get("include_troupe", 1))
        return context

    def form_valid(self, form):
        if hasattr(self, 'valid_message'):
            msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SUCCESS",
                defaults={
                    'summary': "Successful Submission",
                    'description': self.valid_message})
            messages.success(self.request, msg[0].description)
        return_valid = super().form_valid(form)
        return return_valid
