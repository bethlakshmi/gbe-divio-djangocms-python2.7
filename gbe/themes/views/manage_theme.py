from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.models import (
    StyleValue,
    StyleVersion,
    UserMessage,
)
from gbe.themes.forms import ColorStyleValueForm
from django.contrib import messages
from gbetext import user_messages
from datetime import datetime


class ManageTheme(View):
    object_type = StyleVersion
    template = 'gbe/themes/manage_theme.tmpl'
    page_title = 'Manage Style Settings'
    style_version = None

    def groundwork(self, request, args, kwargs):
        self.style_version = None
        version_id = kwargs.get("version_id")
        self.style_version = get_object_or_404(StyleVersion, id=version_id)

    def make_context(self, forms):
        message_code = "THEME_INSTRUCTIONS"
        msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code=message_code,
                defaults={
                    'summary': user_messages[message_code]['summary'],
                    'description': user_messages[message_code]['description']}
                )
        title = "Manage Styles Settings for %s, version %d" % (
            self.style_version.name,
            self.style_version.number)
        context = {
            'instructions': msg[0].description,
            'page_title': self.page_title,
            'title': title,
            'forms': forms,
            'version': self.style_version,
        }
        return context

    def setup_forms(self, request=None):
        forms = []
        for value in StyleValue.objects.filter(
                style_version=self.style_version).order_by(
                'style_property__selector__used_for',
                'style_property__selector__selector',
                'style_property__selector__pseudo_class'):
            if request:
                form = ColorStyleValueForm(request.POST,
                                           instance=value,
                                           prefix=str(value.pk))
            else:
                form = ColorStyleValueForm(instance=value,
                                           prefix=str(value.pk))
            form['value'].label = str(value.style_property.style_property)
            forms += [(value, form)]
        return forms

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageTheme, self).dispatch(*args, **kwargs)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        forms = self.setup_forms()
        return render(request, self.template, self.make_context(forms))

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'cancel' in list(request.POST.keys()):
            messages.success(request, "The last update was canceled.")
            return HttpResponseRedirect(reverse('themes_list',
                                                urlconf='gbe.themes.urls'))
        self.groundwork(request, args, kwargs)
        forms = self.setup_forms(request)
        all_valid = True
        for value, form in forms:
            if not form.is_valid():
                all_valid = False
        if all_valid:
            for value, form in forms:
                form.save()
            self.style_version.updated_at = datetime.now()
            self.style_version.save()
            messages.success(request, "Updated %s" % self.style_version)
            if 'finish' in list(request.POST.keys()):
                return HttpResponseRedirect("%s?changed_id=%d" % (
                    reverse('themes_list', urlconf='gbe.themes.urls'),
                    self.style_version.pk))
        else:
            messages.error(
                request,
                "Something was wrong, correct the errors below and try again.")

        return render(request, self.template, self.make_context(forms))
