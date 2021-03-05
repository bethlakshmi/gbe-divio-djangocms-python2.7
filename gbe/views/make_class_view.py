from gbe.views import MakeBidView
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from gbe.models import (
    Class,
    Persona,
)
from gbe_forms_text import avoided_constraints_popup_text
from gbe.forms import (
    ClassBidForm,
    ClassBidDraftForm,
)
from gbetext import (
    default_class_submit_msg,
    default_class_draft_msg
)
from datetime import timedelta


class MakeClassView(MakeBidView):
    page_title = "Submit a Class"
    view_title = "Submit a Class"
    draft_fields = ['b_title', 'teacher', 'b_description']
    submit_fields = ['b_title',
                     'teacher',
                     'b_description',
                     'schedule_constraints']
    bid_type = "Class"
    has_draft = True
    submit_msg = default_class_submit_msg
    draft_msg = default_class_draft_msg
    submit_form = ClassBidForm
    draft_form = ClassBidDraftForm
    prefix = "theclass"
    bid_class = Class

    def groundwork(self, request, args, kwargs):
        redirect = super(MakeClassView, self).groundwork(request, args, kwargs)
        if redirect:
            return redirect
        self.teachers = self.owner.personae.all()
        if len(self.teachers) == 0:
            return '%s?next=%s' % (
                reverse('persona-add', urlconf='gbe.urls', args=[0]),
                reverse('class_create', urlconf='gbe.urls'))

        if self.bid_object and (
                self.bid_object.teacher.contact != self.owner):
            raise Http404

    def get_initial(self):
        initial = {}
        if not self.bid_object:
            initial = {'owner': self.owner,
                       'teacher': self.teachers[0]}
        return initial

    def set_up_form(self):
        q = Persona.objects.filter(
            performer_profile_id=self.owner.resourceitem_id)
        self.form.fields['teacher'].queryset = q

    def make_context(self, request):
        context = super(MakeClassView, self).make_context(request)
        context['popup_text'] = avoided_constraints_popup_text
        return context

    def set_valid_form(self, request):
        self.bid_object.duration = timedelta(
            minutes=self.bid_object.length_minutes)
        self.bid_object.b_conference = self.conference
        self.bid_object.e_conference = self.conference
        self.bid_object = self.form.save(commit=True)
