from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django_addanother.views import UpdatePopupMixin
from gbe.models import Bio
from django.urls import reverse
from django.http import Http404


class PerformerUpdate(UpdatePopupMixin, PermissionRequiredMixin, RedirectView):
    def has_permission(self):
        return hasattr(self.request.user, 'profile')

    def get_redirect_url(self, *args, **kwargs):
        redirect = reverse('persona-update',
                           urlconf="gbe.urls",
                           args=[kwargs['pk']])
        try:
            performer = Bio.objects.get(pk=kwargs['pk'],
                                        contact__user_object=self.request.user)
        except:
            raise Http404

        if self.is_popup():
            redirect = redirect + "?_popup=1"
        return redirect
