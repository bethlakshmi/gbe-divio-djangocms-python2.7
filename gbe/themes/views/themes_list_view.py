from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from gbe.models import StyleVersion
from gbe.functions import validate_perms


class ThemesListView(View):
    object_type = StyleVersion
    template = 'gbe/themes/theme_list.tmpl'
    title = "List of Themes and Versions"
    permissions = ('Theme Editor',)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ThemesListView, self).dispatch(*args, **kwargs)

    def get_context_dict(self):
        return {
            'title': self.title,
            'page_title': self.title,
            'themes': self.object_type.objects.all(),
            'details_off': True,
            'changed_id': self.changed_id}

    @never_cache
    def get(self, request, *args, **kwargs):
        self.profile = validate_perms(request, self.permissions)
        self.changed_id = int(request.GET.get('changed_id', default=-1))
        return render(request, self.template, self.get_context_dict())
