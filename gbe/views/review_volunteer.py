from django.shortcuts import get_object_or_404
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.contrib import messages
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
)
from gbe.models import (
    Conference,
    Profile,
    VolunteerEvaluation,
    UserMessage,
)
from gbe_utils.mixins import (
    GbeContextMixin,
    FormToTableMixin,
    RoleRequiredMixin,
)
from gbetext import (
    create_vol_eval_msg,
    update_vol_eval_msg,
)


class VolunteerEvalCreate(FormToTableMixin, RoleRequiredMixin, CreateView):
    model = VolunteerEvaluation
    fields = ['vote', 'notes']
    template_name = 'gbe/admin_html_form.tmpl'
    success_url = reverse_lazy('volunteer_review', urlconf="gbe.urls")
    page_title = 'Create Evaluation'
    view_title = 'Create Evaluation'
    valid_message = create_vol_eval_msg
    view_permissions = 'any'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.evaluator = self.request.user.profile
        self.object.volunteer = get_object_or_404(Profile,
                                                  pk=self.kwargs['vol_id'])
        self.object.conference = get_object_or_404(
            Conference,
            conference_slug=self.kwargs['slug'])
        self.object.save()
        return super().form_valid(form)


class VolunteerEvalDelete(DeleteView):
    model = VolunteerEvaluation
    success_url = reverse_lazy('volunteer_review', urlconf="gbe.urls")
    template_name = 'gbe/admin_html_form.tmpl'

    def get_queryset(self):
        return self.model.objects.filter(
            evaluator=self.request.user.profile)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="SUCCESS",
            defaults={'summary': "Successful Delete",
                      'description': "Successfully deleted review for '%s'"})
        messages.success(
            self.request,
            msg[0].description % obj.volunteer.get_badge_name())
        return super().delete(request, *args, **kwargs)


class VolunteerEvalUpdate(FormToTableMixin, UpdateView):
    model = VolunteerEvaluation
    fields = ['vote', 'notes']
    template_name = 'gbe/admin_html_form.tmpl'
    success_url = reverse_lazy('volunteer_review', urlconf="gbe.urls")
    page_title = 'Update Evaluatione'
    view_title = 'Update Evaluation'
    valid_message = update_vol_eval_msg

    def get_queryset(self):
        return self.model.objects.filter(
            evaluator=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_url'] = reverse("volunteer-review-delete",
                                        urlconf="gbe.urls",
                                        args=[self.get_object().pk])
        return context
