from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from ticketing.forms import SignatureForm
from gbe_utils.mixins import (
    GbeFormMixin,
    ProfileRequiredMixin,
)
from ticketing.models import Signature
from gbe.ticketing_idd_interface import get_unsigned_forms
from scheduler.idd import get_schedule
from gbe.functions import (
    get_conference_by_slug,
    get_latest_conference,
    validate_perms,
)
from gbetext import (
    sign_form_msg,
    all_signed_msg,
)


class SignForms(GbeFormMixin, ProfileRequiredMixin, FormView):
    template_name = 'ticketing/sign_forms_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Sign Forms'
    view_title = 'Sign Forms for this Year'
    intro_text = sign_form_msg
    valid_message = all_signed_msg

    def get_initial(self):
        # TODO - what if error?
        if self.request.GET and self.request.GET.get('conf_slug'):
            self.conference = get_conference_by_slug(
                self.request.GET['conf_slug'])
        else:
            self.conference = get_latest_conference()
        self.signer = self.request.user
        if 'user_id' in self.kwargs:
            # sign for other user, only available to registrar
            validate_perms(self.request, ('Registrar', ))
            self.signer = get_object_or_404(User, pk=self.kwargs['user_id'])
            if 'next' in self.request.GET:
                self.success_url = "%s?conf_slug=%s" % (
                    self.request.GET.get('next'),
                    self.conference.conference_slug)
        initial = []
        response = get_schedule(self.signer,
                                labels=[self.conference.conference_slug])
        for item in get_unsigned_forms(self.signer,
                                       self.conference,
                                       response.schedule_items):
            initial += [{'signed_file': item.e_sign_this,
                         'description': item.description}]
        return initial

    def get_form(self):
        kwargs = self.get_form_kwargs()
        SignatureFormSet = modelformset_factory(
            Signature,
            form=SignatureForm,
            extra=0,
            min_num=len(kwargs['initial']),
            validate_min=True)
        return SignatureFormSet(**kwargs, queryset=Signature.objects.none())

    def form_valid(self, form):
        instances = form.save(commit=False)
        custom_msg = None
        for instance in instances:
            instance.user = self.signer
            instance.conference = self.conference
            instance.save()
        if 'user_id' in self.kwargs:
            custom_msg = "  Signatures complete for user %s, conference %s" % (
                str(self.signer.profile),
                self.conference.conference_name)
        return super().form_valid(form, custom_msg=custom_msg)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signer'] = self.signer
        return context

