from django.views.generic.edit import ModelFormMixin
from django.contrib import messages
from gbe.models import UserMessage


class GbeFormMixin(ModelFormMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['view_title'] = self.view_title
        if hasattr(self, 'intro_text'):
            context['intro_text'] = self.intro_text
        context['mode'] = self.mode
        context['include_troupe'] = int(self.kwargs.get("include_troupe", 1))

        return context

    def form_valid(self, form):
        msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="SUCCESS",
            defaults={
                'summary': "Successful Submission",
                'description': self.valid_message})
        messages.success(self.request, msg[0].description)
        return super().form_valid(form)
