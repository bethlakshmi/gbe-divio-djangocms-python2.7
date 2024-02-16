from gbe_utils.mixins import (
    ConferenceListView,
    GbeContextMixin,
    RoleRequiredMixin,
)
from django.contrib.auth.models import (
    Group,
    User,
)
from ticketing.models import Signature
from gbe.ticketing_idd_interface import get_signatories


class ManageSignatures(GbeContextMixin,
                       RoleRequiredMixin,
                       ConferenceListView):
    model = Signature
    template_name = 'ticketing/manage_signatures.tmpl'
    page_title = 'Manage Signatures'
    view_title = 'Manage Signatures'
    intro_text = '''Here are all users who should/did sign forms for this
     year's expo.'''
    context_object_name = 'signatures'
    view_permissions = ('Registrar', )

    def get_queryset(self):
        return self.model.objects.filter(conference=self.conference)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = " - " + self.conference.conference_slug
        context['columns'] = ['Profile',
                              'Signed Forms',
                              'Needs Signing',
                              'Action']
        rows = {}
        signature_needed = get_signatories(self.conference)
        for signature in self.get_queryset():
            if signature.user in rows.keys():
                rows[signature.user]['signatures'] += [signature]
            else:
                rows[signature.user] = {
                    'signatures': [signature],
                    'please_sign': []
                }
        for user, to_be_signed in signature_needed.items():
            if user in rows.keys():
                rows[user]['please_sign'] = to_be_signed
            else:
                rows[user] = {
                    'signatures': [],
                    'please_sign': to_be_signed
                }
        context['rows'] = rows

        return context
