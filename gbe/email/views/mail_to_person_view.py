from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.urls import reverse
from gbe.models import Account as Profile
from gbe.email.views import MailView
from gbe.functions import validate_perms


class MailToPersonView(MailView):
    email_permissions = ['Registrar',
                         'Volunteer Coordinator',
                         'Act Coordinator',
                         'Vendor Coordinator',
                         'Ticketing - Admin',
                         'Scheduling Mavens',
                         'Staff Lead',
                         'Stage Manager',
                         'Technical Director',
                         'Producer']
    email_type = "individual"

    def groundwork(self, request, args, kwargs):
        self.user = validate_perms(request, self.email_permissions)
        user_profile = get_object_or_404(
            Profile,
            resourceitem_id=kwargs.get('profile_id'))
        return [(user_profile.user_object.email, "%s <%s>" % (
            user_profile.display_name,
            user_profile.user_object.email))]

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        to_address = self.groundwork(request, args, kwargs)
        email_form = self.setup_email_form(request, to_address)
        return render(
            request,
            'gbe/email/send_mail.tmpl',
            {"email_form": email_form})

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        to_address = self.groundwork(request, args, kwargs)
        mail_form = self.send_mail(request, to_address)
        if mail_form.is_valid():
            return HttpResponseRedirect(
                reverse('home', urlconf='gbe.urls'))

        else:
            return render(
                request,
                'gbe/email/send_mail.tmpl',
                {"email_form": mail_form})
