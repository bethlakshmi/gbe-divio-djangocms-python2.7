from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.contrib import messages
from gbe.models import (
    Performer,
    UserMessage,
)
from gbe_utils.mixins import ProfileRequiredMixin


class DeletePerformerView(ProfileRequiredMixin, DeleteView):
    model = Performer
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    template_name = 'gbe/modal_performer_form.tmpl'

    def get_queryset(self):
        return self.model.objects.filter(
            contact__user_object=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="SUCCESS",
            defaults={
                'summary': "Successful Delete",
                'description': "Successfully deleted %s"})
        messages.success(self.request, msg[0].description % str(obj))
        data_to_return = super(DeletePerformerView,
                               self).delete(request, *args, **kwargs)
        return data_to_return
