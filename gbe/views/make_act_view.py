from gbe.views import MakeBidView
from django.http import Http404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.forms import ModelChoiceField
from gbe.ticketing_idd_interface import (
    performer_act_submittal_link,
    verify_performer_app_paid,
)
from gbe.models import (
    Act,
    AudioInfo,
    LightingInfo,
    Performer,
    StageInfo,
    TechInfo,
)
from gbe.forms import (
    ActEditDraftForm,
    ActEditForm,
    AudioInfoForm,
    StageInfoForm,
)
from gbetext import (
    default_act_submit_msg,
    default_act_draft_msg,
)
from gbe.views.act_display_functions import display_invalid_act


class MakeActView(MakeBidView):
    page_title = 'Act Proposal'
    view_title = 'Propose an Act'
    draft_fields = ['b_title', 'performer']
    submit_fields = ['b_title',
                     'b_description',
                     'shows_preferences',
                     'performer', ]
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
            redirect_prefix = 'summer_act_'
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

        self.personae = self.owner.personae.all()
        if len(self.personae) == 0:
            return '%s?next=%s' % (
                reverse('persona_create', urlconf='gbe.urls'),
                reverse('act_create', urlconf='gbe.urls'))

        if self.bid_object and (
                self.bid_object.performer.contact != self.owner):
            raise Http404
        self.fee_link = performer_act_submittal_link(request.user.id)

    def get_initial(self):
        initial = {}
        if self.bid_object:
            audio_info = self.bid_object.tech.audio
            stage_info = self.bid_object.tech.stage
            initial = {
                'track_title': audio_info.track_title,
                'track_artist': audio_info.track_artist,
                'track_duration': audio_info.track_duration,
                'act_duration': stage_info.act_duration}
        else:
            initial = {
                'owner': self.owner,
                'performer': self.personae[0],
                'b_conference': self.conference,
                'b_title': "%s Act - %s" % (
                    self.owner,
                    self.conference.conference_slug)}
        return initial

    def set_up_form(self):
        q = Performer.objects.filter(contact=self.owner)
        self.form.fields['performer'] = ModelChoiceField(queryset=q)

    def make_context(self, request):
        context = super(MakeActView, self).make_context(request)
        context['fee_link'] = self.fee_link
        return context

    def check_validity(self, request):
        self.audioform = AudioInfoForm(request.POST, prefix='theact')
        self.stageform = StageInfoForm(request.POST, prefix='theact')
        if hasattr(self.bid_object, 'tech'):
            self.audioform.instance = self.bid_object.tech.audio
            self.stageform.instance = self.bid_object.tech.stage
        return all([self.form.is_valid(),
                    self.audioform.is_valid(),
                    self.stageform.is_valid()])

    def set_valid_form(self, request):
        if not hasattr(self.bid_object, 'tech'):
            techinfo = TechInfo()
            lightinginfo = LightingInfo()
            lightinginfo.save()
            techinfo.lighting = lightinginfo
        else:
            techinfo = self.bid_object.tech

        techinfo.audio = self.audioform.save()
        techinfo.stage = self.stageform.save()
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

    def fee_paid(self):
        return verify_performer_app_paid(
            self.owner.user_object.username,
            self.conference)
