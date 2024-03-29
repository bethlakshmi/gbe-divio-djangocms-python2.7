from gbe.views import MakeBidView
from django.http import Http404
from django.urls import reverse
from django.shortcuts import render
from gbe.forms import (
    CostumeBidDraftForm,
    CostumeDetailsDraftForm,
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
)
from gbe.models import (
    Costume,
    Bio,
    UserMessage
)
from gbe_forms_text import (
    costume_proposal_labels,
    costume_proposal_form_text,
)
from gbetext import (
    default_costume_submit_msg,
    default_costume_draft_msg
)


class MakeCostumeView(MakeBidView):
    page_title = "Displaying a Costume"
    view_title = "Displaying a Costume"
    draft_fields = ['b_title', 'creator', 'first_name', 'last_name', 'phone']
    submit_fields = [
        'b_title',
        'creator',
        'active_use',
        'pieces',
        'b_description',
        'pasties',
        'dress_size',
        'picture']
    bid_type = "Costume"
    has_draft = True
    submit_msg = default_costume_submit_msg
    draft_msg = default_costume_draft_msg
    submit_form = CostumeBidSubmitForm
    draft_form = CostumeBidDraftForm
    prefix = None
    bid_class = Costume
    instructions = costume_proposal_form_text

    def groundwork(self, request, args, kwargs):
        redirect = super(
            MakeCostumeView,
            self).groundwork(request, args, kwargs)
        if redirect:
            return redirect
        self.performers = self.owner.bio_set.all()
        if len(self.performers) == 0:
            return '%s?next=%s' % (
                reverse('persona-add', urlconf='gbe.urls'),
                reverse('costume_create', urlconf='gbe.urls'))

        if self.bid_object and ((self.bid_object.profile != self.owner) or (
                self.bid_object.bio not in self.performers)):
            raise Http404

    def get_initial(self):
        initial = super(MakeCostumeView, self).get_initial()
        if not self.bid_object:
            initial.update({'profile': self.owner,
                            'performer': self.performers[0]})
        return initial

    def make_post_forms(self, request, the_form):
        if the_form == self.submit_form:
            details_form = CostumeDetailsSubmitForm
        else:
            details_form = CostumeDetailsDraftForm

        if not self.bid_object:
            self.bid_object = self.bid_class()

        self.form = the_form(
            request.POST,
            instance=self.bid_object,
            initial=self.get_initial(),
            prefix=self.prefix)
        self.details_form = details_form(
            request.POST,
            request.FILES,
            instance=self.bid_object)

    def get_create_form(self, request):
        if self.bid_object:
            self.form = self.submit_form(
                prefix=self.prefix,
                instance=self.bid_object,
                initial=self.get_initial())
            self.details_form = CostumeDetailsSubmitForm(
                instance=self.bid_object)
        else:
            self.form = self.submit_form(
                prefix=self.prefix,
                initial=self.get_initial())
            self.details_form = CostumeDetailsSubmitForm()
        self.set_up_form()

        return render(
            request,
            'gbe/bid.tmpl',
            self.make_context(request)
        )

    def set_up_form(self):
        self.form.fields['bio'].queryset = self.owner.bio_set.all()

    def make_context(self, request):
        context = super(MakeCostumeView, self).make_context(request)
        context['forms'] = [self.form, self.details_form]
        return context

    def check_validity(self, request):
        return self.form.is_valid() and self.details_form.is_valid()

    def set_valid_form(self, request):
        self.bid_object.profile = self.owner
        self.bid_object.b_conference = self.conference
        self.bid_object = self.form.save()
        self.bid_object = self.details_form.save()
