from django.views.generic.edit import ContextMixin
from gbe.models import UserMessage


class GbeContextMixin(ContextMixin):

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

        return context
