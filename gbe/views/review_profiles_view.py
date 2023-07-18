from django.views.generic import ListView
from gbe_utils.mixins import (
    GbeContextMixin,
    RoleRequiredMixin,
)
from django.urls import reverse
from gbe.models import (
    Bio,
    Profile,
    UserMessage,
)
from gbe.functions import validate_perms
from settings import GBE_TABLE_FORMAT
from gbetext import profile_intro_msg


class ReviewProfilesView(GbeContextMixin, RoleRequiredMixin, ListView):
    model = Profile
    template_name = 'gbe/profile_review.tmpl'
    page_title = 'Manage Users'
    view_title = 'Manage Users'
    intro_text = profile_intro_msg
    view_permissions = ('Registrar',
                        'Volunteer Coordinator',
                        'Vendor Coordinator',
                        'Scheduling Mavens',
                        'Act Coordinator',
                        'Class Coordinator',
                        'Ticketing - Admin',
                        'Staff Lead')

    def get_queryset(self):
        return self.model.objects.filter(user_object__is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['columns'] = ['Name',
                              'Username',
                              'Last Login',
                              'Contact Info',
                              'Action']
        context['merge_users'] = True
        rows = []
        for aprofile in self.get_queryset():
            bid_row = {}
            last_login = "NEVER LOGGED IN"
            if aprofile.user_object.last_login:
                last_login = aprofile.user_object.last_login.strftime(
                    GBE_TABLE_FORMAT)
            display_name = aprofile.display_name
            for performer in Bio.objects.filter(contact=aprofile):
                perf_addon = "<br>Performer - %s"
                if performer.multiple_performers:
                    perf_addon = "<br>Troupe - %s"
                display_name += perf_addon % performer.name
            bid_row['profile'] = (
                display_name,
                aprofile.user_object.username,
                last_login)
            bid_row['contact_info'] = {
                'contact_email': aprofile.user_object.email,
                'purchase_email': aprofile.purchase_email,
                'phone': aprofile.phone
            }
            bid_row['id'] = aprofile.pk
            bid_row['actions'] = [
                {'url': reverse('admin_landing_page',
                                urlconf='gbe.urls',
                                args=[aprofile.pk]),
                 'text': "View Landing Page"},
                {'url': reverse('welcome_letter',
                                urlconf='gbe.reporting.urls',
                                args=[aprofile.pk]),
                 'text': "Welcome Letter"},
                {'url': reverse(
                    'mail_to_individual',
                     urlconf='gbe.email.urls',
                     args=[aprofile.pk]),
                 'text': "Email"}]
            if 'Registrar' in self.request.user.profile.privilege_groups:
                bid_row['actions'] += [
                    {'url': "%s?next=%s" % (reverse(
                        'admin_profile',
                        urlconf='gbe.urls',
                        args=[aprofile.pk]), self.request.path),
                     'text': "Update"}]
                bid_row['actions'] += [
                    {'url': reverse('delete_profile',
                                    urlconf='gbe.urls',
                                    args=[aprofile.pk]),
                     'text': "Delete"}]

            rows.append(bid_row)
        context['rows'] = rows
        context['order'] = 0
        return context
