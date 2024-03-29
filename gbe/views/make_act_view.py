from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from gbe.views import MakeBidView
from gbe.models import (
    Act,
    TechInfo,
    UserMessage,
)
from gbe.forms import (
    ActEditDraftForm,
    ActEditForm,
)
from gbetext import (
    act_not_unique,
    default_act_title_conflict,
    default_act_submit_msg,
    default_act_draft_msg,
)


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
                     'num_performers',
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

        self.bios = self.owner.bio_set.all()
        if len(self.bios) == 0:
            return '%s?next=%s' % (
                reverse('persona-add', urlconf='gbe.urls'),
                reverse('act_create', urlconf='gbe.urls'))

        if self.bid_object and (
                self.bid_object.performer.contact != self.owner):
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
                'performer': self.bios[0],
                'b_conference': self.conference})
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
        if [act_not_unique] in list(self.form.errors.values()):
            conflict_msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="ACT_TITLE_CONFLICT",
                defaults={
                    'summary': "Act Title, User, Conference Conflict",
                     'description': default_act_title_conflict})
            conflict = Act.objects.filter(
                b_conference=self.conference,
                b_title=self.form.data['theact-b_title'],
                bio__contact=self.owner).first()
            if conflict.submitted:
                link = reverse('act_view',
                               urlconf='gbe.urls',
                               args=[conflict.pk])
            else:
                link = reverse('act_edit',
                               urlconf='gbe.urls',
                               args=[conflict.pk])
            messages.error(
                request, conflict_msg[0].description % (
                    link,
                    conflict.b_title))
        return render(request, 'gbe/bid.tmpl', self.make_context(request))
