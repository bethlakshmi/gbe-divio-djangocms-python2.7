from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe.models import (
    StyleVersion,
    UserMessage,
)
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from gbetext import user_messages


class DeleteTheme(View):
    object_type = StyleVersion

    def groundwork(self, request, args, kwargs):
        self.style_version = None
        version_id = kwargs.get("version_id")
        self.style_version = get_object_or_404(StyleVersion, id=version_id)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteTheme, self).dispatch(*args, **kwargs)

    @never_cache
    def get(self, request, *args, **kwargs):
        theme_display = "%s"
        self.groundwork(request, args, kwargs)
        if StyleVersion.objects.all().count() == 1:
            error_code = "LAST_THEME"
            msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code=error_code,
                defaults={
                    'summary': user_messages[error_code]['summary'],
                    'description': user_messages[error_code]['description']})
            messages.error(
                request,
                msg[0].description + "  TARGET: " + str(self.style_version))
            theme_display = "%s?error_id=" + str(self.style_version.pk)
        elif self.style_version.currently_live or (
                self.style_version.currently_test):
            error_code = "CURRENTLY_ACTIVE"
            msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code=error_code,
                defaults={
                    'summary': user_messages[error_code]['summary'],
                    'description': user_messages[error_code]['description']})
            messages.error(
                request,
                msg[0].description + "  TARGET: " + str(self.style_version))
            theme_display = "%s?error_id=" + str(self.style_version.pk)
        else:
            self.style_version.delete()
            messages.success(
                request,
                "Deleted Theme %s" % str(self.style_version))
        return HttpResponseRedirect(theme_display % (
            reverse('themes_list', urlconf='gbe.themes.urls')))
