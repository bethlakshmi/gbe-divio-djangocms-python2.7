from django.views.generic.list import ListView
from gbe_utils.mixins import (
    GbeContextMixin,
    ProfileRequiredMixin,
)
from django.contrib.auth.models import (
    Group,
    User,
)
from ticketing.models import Signature


class SignatureList(GbeContextMixin, ProfileRequiredMixin, ListView):
    model = Signature
    template_name = 'ticketing/signatures.tmpl'
    page_title = 'Signed Forms'
    view_title = 'Signed Forms from All Expos'
    intro_text = '''Here are all the forms you've signed'''
    context_object_name = 'signatures'


    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


    def get_context_data(self, **kwargs):
        from gbe.special_privileges import special_menu_tree
        context = super().get_context_data(**kwargs)
        context['columns'] = ['Form',
                              'Conference',
                              'Signed On',
                              'Name Signed']
        return context
