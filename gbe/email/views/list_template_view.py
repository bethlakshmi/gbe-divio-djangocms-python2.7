from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from gbe.functions import validate_perms
from gbe.email.functions import get_user_email_templates


class ListTemplateView(View):
    page_title = 'Manage Email Templates'
    view_title = 'Choose a Template'
    reviewer_permissions = ['Act Coordinator',
                            'Class Coordinator',
                            'Costume Coordinator',
                            'Registrar',
                            'Scheduling Mavens',
                            'Vendor Coordinator',
                            'Volunteer Coordinator',
                            ]

    def groundwork(self, request, args, kwargs):
        self.user = validate_perms(request, self.reviewer_permissions)

    @method_decorator(never_cache, name="get")
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return render(
            request,
            'gbe/email/list_email_template.tmpl',
            {"email_templates": get_user_email_templates(self.user),
             "page_title": self.page_title,
             "view_title": self.view_title, }
            )

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListTemplateView, self).dispatch(*args, **kwargs)
