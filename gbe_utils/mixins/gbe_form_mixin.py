from gbe_utils.mixins import SubwayMapMixin
from django.views.generic.edit import ModelFormMixin
from django.contrib import messages
from gbe.models import UserMessage


class GbeFormMixin(SubwayMapMixin, ModelFormMixin):
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
        context['mode'] = self.mode
        if hasattr(self, 'no_tabs'):
            context['no_tabs'] = self.no_tabs
        else:
            context['include_troupe'] = int(
                self.kwargs.get("include_troupe", 1))
        context['return_url'] = self.success_url
        context['subway_map'] = self.make_map(self.__class__.__name__,
                                              self.get_success_url())
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
