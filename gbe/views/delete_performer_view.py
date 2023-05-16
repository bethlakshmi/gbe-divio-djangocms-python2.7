from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.http import HttpResponseRedirect
from gbe.models import (
    Performer,
    UserMessage,
)
from gbe_utils.mixins import ProfileRequiredMixin
from gbetext import delete_in_use


class DeletePerformerView(ProfileRequiredMixin, DeleteView):
    model = Performer
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    template_name = 'gbe/modal_performer_form.tmpl'

    def get_queryset(self):
        return self.model.objects.filter(
            contact__user_object=self.request.user)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.has_bids():
            msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="DELETED_IN_USE_PERFORMER",
                defaults={
                    'summary': "Delete In Use Performer Error",
                    'description': delete_in_use})
            messages.error(self.request, msg[0].description)
            return HttpResponseRedirect(
                request.META.get('HTTP_REFERER', self.success_url))
        else:
            msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SUCCESS",
                defaults={
                    'summary': "Successful Delete",
                    'description': "Successfully deleted persona %s"})
            messages.success(self.request, msg[0].description % str(obj))
        return super(DeletePerformerView,
                     self).delete(request, *args, **kwargs)
