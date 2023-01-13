from gbe_utils.mixins import GbeFormMixin
from django.contrib import messages
from gbe.models import UserMessage
from django.forms import modelformset_factory
from gbe.forms import SocialLinkForm
from gbe.models import SocialLink


class SocialLinkMixin(GbeFormMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        SocialLinkForms = modelformset_factory(
            SocialLink,
            form=SocialLinkForm,
            max_num=5,
            extra=5)
        context["sociallinkformset"] = SocialLinkForms(
            queryset=SocialLink.objects.filter(performer=self.object))
        return context

    def form_valid(self, form):
        return super().form_valid(form)
