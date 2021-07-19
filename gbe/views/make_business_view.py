from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from gbe_utils.mixins import (
    GbeFormMixin,
    ProfileRequiredMixin,
)
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from gbe.models import Business
from gbe.forms import BusinessForm
from django.urls import reverse_lazy
from gbetext import (
    default_create_business_msg,
    default_edit_business_msg,
)


class BusinessCreate(CreatePopupMixin,
                     GbeFormMixin,
                     ProfileRequiredMixin,
                     CreateView):
    model = Business
    form_class = BusinessForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Business'
    view_title = 'Tell Us About Your Business'
    mode = "performer"
    valid_message = default_create_business_msg
    no_tabs = True

    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.owners.add(self.request.user.profile)
        return response


class BusinessUpdate(UpdatePopupMixin,
                     GbeFormMixin,
                     ProfileRequiredMixin,
                     UpdateView):
    model = Business
    form_class = BusinessForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Business'
    view_title = 'Tell Us About Your Business'
    mode = "update"
    valid_message = default_edit_business_msg
    no_tabs = True

    def get_queryset(self):
        return self.model.objects.filter(
            owners__user_object=self.request.user)
