from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.forms import modelformset_factory
from ticketing.forms import SignatureForm
from gbe_utils.mixins import (
    GbeFormMixin,
    ProfileRequiredMixin,
)
from ticketing.models import Signature
from gbe.ticketing_idd_interface import get_unsigned_forms
from scheduler.idd import get_schedule
from gbe.functions import get_latest_conference
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
        self.conference = get_latest_conference()
        initial = []
        response = get_schedule(self.request.user,
                                labels=[self.conference.conference_slug])
        for item in get_unsigned_forms(self.request.user,
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
        for instance in instances:
            instance.user = self.request.user
            instance.conference = self.conference
            instance.save()
        return super().form_valid(form)
