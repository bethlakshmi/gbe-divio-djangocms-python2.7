from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.views.generic import UpdateView
from gbe_utils.mixins import (
    GbeFormMixin,
    RoleRequiredMixin,
)
from gbetext import (
    edit_package_message,
    ticket_package_intro,
)
from ticketing.models import TicketPackage
from ticketing.forms import TicketPackageForm
from gbe.models import UserMessage


class TicketPackageUpdate(GbeFormMixin, RoleRequiredMixin, UpdateView):
    model = TicketPackage
    form_class = TicketPackageForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('ticket_items', urlconf='ticketing.urls')
    page_title = "Edit Package Type"
    view_title = "Edit Package Type"
    valid_message = edit_package_message
    intro_text = ticket_package_intro
    view_permissions = ('Ticketing - Admin', )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_url'] = reverse(
            "ticket_item_edit",
            urlconf="ticketing.urls",
            args=[self.get_object().pk]) + "?delete_item=True"
        return context

    def form_valid(self, form):
        self.object = form.save(str(self.request.user))
        if hasattr(self, 'valid_message'):
            msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SUCCESS",
                defaults={
                    'summary': "Successful Submission",
                    'description': self.valid_message})
            messages.success(self.request, "%s  Package Id: %s, Title: %s" % (
                msg[0].description,
                self.object.ticket_id,
                self.object.title))
        return HttpResponseRedirect(self.get_success_url() + (
            "?updated_tickets=[%s]&open_panel=ticket" % self.object.pk))
