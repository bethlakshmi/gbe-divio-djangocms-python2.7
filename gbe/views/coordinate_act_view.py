from gbe.views import MakeActView
from dal import autocomplete
from django.http import Http404
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect
from gbe.models import (
    Act,
    Performer,
    TechInfo,
)
from gbe.views.act_display_functions import display_invalid_act
import datetime


class CoordinateActView(PermissionRequiredMixin, MakeActView):
    page_title = 'Create Act for Coordinator'
    view_title = 'Book an Act'
    has_draft = False
    permission_required = 'gbe.assign_act'

    def groundwork(self, request, args, kwargs):
        # do the basic bid stuff, but NOT the regular act stuff
        redirect = super(MakeActView, self).groundwork(request, args, kwargs)
        if redirect:
            return redirect

    def set_up_form(self):
        self.form.fields['performer'].widget = autocomplete.ModelSelect2(
            url='coordinator-performer-autocomplete')
        self.form.fields['performer'].queryset = Performer.objects.all()

    def get_initial(self):
        return {'b_conference': self.conference}
