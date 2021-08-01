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
from gbe.themes.views import ManageTheme
from gbe.models import (
    StyleValue,
    StyleVersion,
    UserMessage,
)
from gbe.themes.forms import (
    StyleValueForm,
    StyleValueImageForm,
    ThemeVersionForm,
)
from django.contrib import messages
from gbetext import user_messages


class CloneTheme(ManageTheme):
    page_title = 'Clone Style Settings'
    title_format = "Clone Styles Settings for {}, version {:.1f}"
    instruction_code = "CLONE_INSTRUCTIONS"

    def make_context(self, version_form, forms, group_forms):
        context = super(CloneTheme, self).make_context(forms, group_forms)
        context['version_form'] = version_form
        return context

    def make_single_form(self, request, form_type, value):
        if request.POST:
            form = form_type(request.POST,
                             request.FILES,
                             initial={'value': value.value,
                                      'image': value.image,
                                      'style_property': value.style_property},
                             prefix=str(value.pk))
        else:
            form = form_type(instance=value, prefix=str(value.pk))
        return form

    def setup_forms(self, request):
        if request.POST:
            version_form = ThemeVersionForm(request.POST)
        else:
            version_form = ThemeVersionForm()
        forms, group_forms = super(CloneTheme, self).setup_forms(request)
        return (version_form, forms, group_forms)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        (version_form, forms, group_forms) = self.setup_forms(request)
        return render(request,
                      self.template,
                      self.make_context(version_form, forms, group_forms))

    def forms_and_context(self, request):
        (version_form, forms, group_forms) = self.setup_forms(request)
        if not version_form.is_valid():
            messages.error(
                "Theme setup information is not correct, see form for errors")
        return self.make_context(version_form, forms, group_forms)

    def process_forms(self, context):
        new_version = context['version_form'].save()
        for value, form in context['forms']:
            instance = form.save(commit=False)
            instance.style_version = new_version
            instance.save()
        for label, label_forms in context['group_forms'].items():
            for element, element_form in label_forms.items():
                for table_form in element_form:
                    instance = table_form.save(commit=False)
                    instance.style_version = new_version
                    instance.save()
        return (new_version.pk,
                "Cloned %s from %s" % (new_version, self.style_version))
