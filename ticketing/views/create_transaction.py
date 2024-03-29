from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from datetime import datetime
from gbe_utils.mixins import (
    FormToTableMixin,
    RoleRequiredMixin,
)
from ticketing.models import (
    Purchaser,
    Transaction,
)
from ticketing.forms import CompFeeForm
from gbetext import (
    create_comp_msg,
)


class CreateTransaction(FormToTableMixin, RoleRequiredMixin, CreateView):
    model = Transaction
    form_class = CompFeeForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('transactions', urlconf="ticketing.urls")
    page_title = 'Create Transaction'
    view_title = 'Create Comp Fee'
    valid_message = create_comp_msg
    view_permissions = ('Ticketing - Transactions', )

    def form_valid(self, form):
        form.instance.amount = 0
        form.instance.order_date = datetime.now()
        form.instance.payment_source = "GBE comp"
        form.instance.amount = 0
        profile = form.cleaned_data['profile']
        if profile.user_object.purchaser_set.exists():
            form.instance.purchaser = profile.user_object.purchaser_set.first()
        else:
            purchaser = Purchaser(
                matched_to_user=profile.user_object,
                first_name=profile.user_object.first_name,
                last_name=profile.user_object.last_name,
                email=profile.user_object.email)
            purchaser.save()
            form.instance.purchaser = purchaser

        return super().form_valid(form)
