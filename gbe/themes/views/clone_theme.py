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

    def setup_forms(self, request):
        forms = []
        group_forms = {}
        if request.POST:
            version_form = ThemeVersionForm(request.POST)
        else:
            version_form = ThemeVersionForm()

        for value in StyleValue.objects.filter(
                style_version=self.style_version).order_by(
                'style_property__selector__used_for',
                'style_property__selector__selector',
                'style_property__selector__pseudo_class',
                'style_property__style_property'):
            form_type = StyleValueForm
            if value.style_property.value_type == "image":
                form_type = StyleValueImageForm
            try:
                if request.POST:
                    form = form_type(
                        request.POST,
                        request.FILES,
                        initial={'value': value.value,
                                 'image': value.image,
                                 'style_property': value.style_property},
                        prefix=str(value.pk))
                else:
                    form = form_type(instance=value,
                                     prefix=str(value.pk))
                if value.style_property.element is not None and (
                        value.style_property.label is not None):
                    if value.style_property.label in group_forms:
                        if value.style_property.element in group_forms[
                                value.style_property.label]:
                            group_forms[value.style_property.label][
                                value.style_property.element] += [form]
                        else:
                            group_forms[value.style_property.label][
                                value.style_property.element] = [form]
                    else:
                        group_forms[value.style_property.label] = {
                            value.style_property.element: [form]}
                else:
                    forms += [(value, form)]
            except Exception as e:
                messages.error(request, e)
        return (version_form, forms, group_forms)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        (version_form, forms, group_forms) = self.setup_forms(request)
        return render(request,
                      self.template,
                      self.make_context(version_form, forms, group_forms))

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'cancel' in list(request.POST.keys()):
            messages.success(request, "The last update was canceled.")
            return HttpResponseRedirect(reverse('themes_list',
                                                urlconf='gbe.themes.urls'))
        self.groundwork(request, args, kwargs)
        (version_form, forms, group_forms) = self.setup_forms(request)
        all_valid = version_form.is_valid()
        if len(messages.get_messages(request)) > 0:
            all_valid = False
        for value, form in forms:
            if not form.is_valid():
                all_valid = False
        if all_valid:
            new_version = version_form.save()
            for value, form in forms:
                instance = form.save(commit=False)
                instance.style_version = new_version
                instance.save()
            messages.success(request, "Cloned %s from %s" % (
                new_version,
                self.style_version))
            if 'update' in list(request.POST.keys()):
                return HttpResponseRedirect(
                    reverse('manage_theme',
                            urlconf='gbe.themes.urls',
                            args=[new_version.pk]))
            else:
                return HttpResponseRedirect("%s?changed_id=%d" % (
                    reverse('themes_list', urlconf='gbe.themes.urls'),
                    new_version.pk))
        else:
            messages.error(
                request,
                "Something was wrong, correct the errors below and try again.")

        return render(request,
                      self.template,
                      self.make_context(version_form, forms, group_forms))
