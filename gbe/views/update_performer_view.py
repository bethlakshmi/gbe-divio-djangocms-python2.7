from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_addanother.views import CreatePopupMixin
from gbe.models import Performer
from django.urls import reverse

class PerformerUpdate(CreatePopupMixin, PermissionRequiredMixin, RedirectView):
    def has_permission(self):
        return hasattr(self.request.user, 'profile')

    def get_redirect_url(self, *args, **kwargs):
        redirect = reverse('performer-update',
                           urlconf="gbe.urls",
                           args=[kwargs['pk']])
        performer = Performer.objects.get_subclass(
            pk=kwargs['pk'],
            contact__user_object=self.request.user)
        if performer.__class__.__name__ == "Troupe":
            redirect = reverse('troupe-update',
                               urlconf="gbe.urls",
                               args=[kwargs['pk']])
        return redirect
