from gbe.views import MakeBidView
from django.http import Http404
from django.urls import reverse
from django.http import HttpResponseRedirect
from gbe.models import (
    Act,
    Bio,
    TechInfo,
)
from gbe.forms import (
    ActEditDraftForm,
    ActEditForm,
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
)
from gbe.views.act_display_functions import display_invalid_act


class MakeActView(MakeBidView):
    page_title = 'Act Proposal'
    view_title = 'Propose an Act'
    draft_fields = ['b_title',
                    'b_description',
                    'bio',
                    'first_name',
                    'last_name',
                    'phone']
    submit_fields = ['b_title',
                     'b_description',
                     'shows_preferences',
                     'bio', ]
    bid_type = "Act"
    has_draft = True
    submit_msg = default_act_submit_msg
    draft_msg = default_act_draft_msg
    submit_form = ActEditForm
    draft_form = ActEditDraftForm
    prefix = "theact"
    bid_class = Act

    def groundwork(self, request, args, kwargs):
        redirect = super(MakeActView, self).groundwork(request, args, kwargs)
        if redirect:
            return redirect

        redirect_prefix = None
        # first, diagnose if we have a act/view mismatch
        if self.conference.act_style == "summer" and (
                self.__class__.__name__ == "MakeActView"):
            redirect_prefix = 'summeract_'
        elif self.conference.act_style == "normal" and (
                self.__class__.__name__ == "MakeSummerActView"):
            redirect_prefix = 'act_'

        # then determine where to reverse
        if redirect_prefix and self.bid_object:
            return reverse(
                "%sedit" % redirect_prefix,
                urlconf='gbe.urls',
                args=[self.bid_object.pk])
        elif redirect_prefix:
            return reverse(
                "%screate" % redirect_prefix,
                urlconf='gbe.urls')

        self.bios = self.owner.bio_set.all()
        if len(self.bios) == 0:
            return '%s?next=%s' % (
                reverse('persona-add', urlconf='gbe.urls', args=[1]),
                reverse('act_create', urlconf='gbe.urls'))

        if self.bid_object and (
                self.bid_object.bio.contact != self.owner):
            raise Http404

    def get_initial(self):
        initial = super(MakeActView, self).get_initial()
        if self.bid_object:
            initial.update({
                'track_title': self.bid_object.tech.track_title,
                'track_artist': self.bid_object.tech.track_artist,
                'act_duration': self.bid_object.tech.duration})
        else:
            initial.update({
                'bio': self.bios[0],
                'b_conference': self.conference,
                'b_title': "%s Act - %s" % (
                    self.owner,
                    self.conference.conference_slug)})
        return initial

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
        self.bid_object.submitted = False
        self.bid_object.accepted = False
        self.bid_object.save()
        self.form.save()

    def get_invalid_response(self, request):
        return display_invalid_act(
            request,
            self.make_context(request),
            self.form,
            self.conference,
            self.owner,
            'MakeActView')
