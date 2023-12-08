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
    edit_ticket_message,
    ticket_type_intro,
)
from ticketing.models import TicketType
from ticketing.forms import TicketTypeForm
from gbe.models import UserMessage


class TicketTypeUpdate(GbeFormMixin, RoleRequiredMixin, UpdateView):
    model = TicketType
    form_class = TicketTypeForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('ticket_items', urlconf='ticketing.urls')
    page_title = "Edit Ticket Type"
    view_title = "Edit Ticket Type"
    valid_message = edit_ticket_message
    intro_text = ticket_type_intro
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
            messages.success(
                self.request,
                "%s  Ticket Type Id: %s, Title: %s" % (msg[0].description,
                                                       self.object.ticket_id,
                                                       self.object.title))
        return HttpResponseRedirect(self.get_success_url() + (
            "?updated_tickets=[%s]" % self.object.pk))
