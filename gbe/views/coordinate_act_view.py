from gbe.views import MakeActView
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin
from gbe.models import TechInfo
from gbe.forms import ActCoordinationForm
from gbetext import act_coord_instruct
from gbe.ticketing_idd_interface import comp_act


class CoordinateActView(PermissionRequiredMixin, MakeActView):
    page_title = 'Create Act for Coordinator'
    view_title = 'Book an Act'
    has_draft = False
    permission_required = 'gbe.assign_act'
    submit_form = ActCoordinationForm
    coordinated = True
    instructions = act_coord_instruct

    def groundwork(self, request, args, kwargs):
        # do the basic bid stuff, but NOT the regular act stuff
        redirect = super(MakeActView, self).groundwork(request, args, kwargs)
        if redirect:
            return redirect

    def get_initial(self):
        return {'b_conference': self.conference}

    def set_valid_form(self, request):
        if not hasattr(self.bid_object, 'tech'):
            techinfo = TechInfo()
        else:
            techinfo = self.bid_object.tech

        techinfo.duration = self.form.cleaned_data['act_duration']
        techinfo.track_title = self.form.cleaned_data['track_title']
        techinfo.track_artist = self.form.cleaned_data['track_artist']
        techinfo.save()
        self.bid_object.tech = techinfo
        self.bid_object.save()
        self.form.save()
        comp_act(self.bid_object.performer.contact.user_object,
                 self.conference)

    def make_context(self, request):
        context = super(MakeActView, self).make_context(request)
        context['nodraft'] = "Submit & Proceed to Casting"
        return context

    def submit_bid(self, request):
        self.bid_object.submitted = True
        self.bid_object.save()
        return reverse('act_review',
                       urlconf="gbe.urls",
                       args=[self.bid_object.id])
