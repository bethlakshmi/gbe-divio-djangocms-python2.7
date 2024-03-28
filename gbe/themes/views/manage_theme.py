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
    StyleGroup,
    StyleValue,
    StyleVersion,
    UserMessage,
)
from gbe.themes.forms import (
    StyleValueForm,
    StyleValueImageForm,
)
from django.contrib import messages
from gbetext import user_messages
from datetime import datetime
from gbe.functions import validate_perms


class ManageTheme(View):
    object_type = StyleVersion
    template = 'gbe/themes/manage_theme.tmpl'
    page_title = 'Manage Style Settings'
    style_version = None
    permissions = ('Theme Editor',)
    title_format = "Manage {}, version {:.1f}"
    instruction_code = "THEME_INSTRUCTIONS"

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        self.style_version = None
        version_id = kwargs.get("version_id")
        self.style_version = get_object_or_404(StyleVersion, id=version_id)

    def make_context(self, request):
        forms, group_forms = self.setup_forms(request)
        msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code=self.instruction_code,
            defaults={
                'summary': user_messages[self.instruction_code]['summary'],
                'description': user_messages[self.instruction_code][
                    'description']})
        title = self.title_format.format(self.style_version.name,
                                         self.style_version.number)
        groups = []
        for group in StyleGroup.objects.all():
            group_dict = {
                'group': group,
                'elements': group.styleelement_set.all().order_by('order'),
                'labels': group.stylelabel_set.all().order_by('order'),
            }
            groups += [group_dict]
        context = {
            'instructions': msg[0].description,
            'page_title': self.page_title,
            'title': title,
            'forms': forms,
            'group_forms': group_forms,
            'version': self.style_version,
            'groups': groups,
        }
        return context

    def make_single_form(self, request, form_type, value):
        if request.POST:
            form = form_type(request.POST,
                             request.FILES,
                             instance=value,
                             prefix=str(value.pk))
        else:
            form = form_type(instance=value, prefix=str(value.pk))
        return form

    def setup_forms(self, request):
        forms = []
        group_forms = {}
        for value in StyleValue.objects.filter(
                style_version=self.style_version,
                style_property__hidden=False).order_by(
                'style_property__selector__used_for',
                'style_property__selector__selector',
                'style_property__selector__pseudo_class',
                'style_property__style_property'):
            form_type = StyleValueForm
            if value.style_property.value_type == "image":
                form_type = StyleValueImageForm
            try:
                form = self.make_single_form(request, form_type, value)
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

        return forms, group_forms

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageTheme, self).dispatch(*args, **kwargs)

    @method_decorator(never_cache, name="get")
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return render(request,
                      self.template,
                      self.make_context(request))

    def process_forms(self, context):
        for value, form in context['forms']:
            form.save()
        for label, label_forms in context['group_forms'].items():
            for element, element_form in label_forms.items():
                for table_form in element_form:
                    table_form.save()
        self.style_version.updated_at = datetime.now()
        self.style_version.save()
        return (self.style_version.pk, "Updated %s" % self.style_version)

    @method_decorator(never_cache, name="post")
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if 'cancel' in list(request.POST.keys()):
            messages.success(request, "The last update was canceled.")
            return HttpResponseRedirect(reverse('themes_list',
                                                urlconf='gbe.themes.urls'))
        self.groundwork(request, args, kwargs)
        context = self.make_context(request)
        all_valid = True
        if len(messages.get_messages(request)) > 0:
            all_valid = False

        for value, form in context['forms']:
            if not form.is_valid():
                all_valid = False
        for label, label_forms in context['group_forms'].items():
            for element, element_form in label_forms.items():
                for table_form in element_form:
                    if not table_form.is_valid():
                        all_valid = False

        if all_valid:
            version_pk, success_msg = self.process_forms(context)
            messages.success(request, success_msg)

            if 'update' in list(request.POST.keys()):
                return HttpResponseRedirect(reverse(
                    'manage_theme',
                    urlconf='gbe.themes.urls',
                    args=[version_pk]))
            else:
                return HttpResponseRedirect("%s?changed_id=%d" % (
                    reverse('themes_list', urlconf='gbe.themes.urls'),
                    version_pk))
        else:
            messages.error(
                request,
                "Something was wrong, correct the errors below and try again.")

        return render(request,
                      self.template,
                      context)
