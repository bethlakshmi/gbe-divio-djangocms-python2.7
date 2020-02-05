from gbe.scheduling.views import ManageVolWizardView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.contrib import messages
from gbe.models import UserMessage
from django.core.urlresolvers import reverse
from gbe.models import (
    StaffArea,
)
from gbe.scheduling.forms import StaffAreaForm
from gbe.functions import validate_perms


class EditStaffAreaView(ManageVolWizardView):
    template = 'gbe/scheduling/edit_event.tmpl'
    permissions = ('Scheduling Mavens',)

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        if "staff_id" in kwargs:
            self.staff_area = get_object_or_404(
                StaffArea,
                id=int(kwargs['staff_id']))
        self.conference = self.staff_area.conference
        self.manage_vol_url = reverse('manage_vol',
                                      urlconf='gbe.scheduling.urls',
                                      args=[self.staff_area.id])
        self.labels = [self.staff_area.slug]
        self.success_url = reverse('edit_staff',
                                   urlconf='gbe.scheduling.urls',
                                   args=[self.staff_area.id])

    def make_context(self, request, errorcontext=None):
        context = super(EditStaffAreaView,
                        self).make_context(request, errorcontext)
        context['edit_title'] = 'Edit Staff Area'
        context['staff_id'] = self.staff_area.pk

        # if there was an error in the edit form
        if 'event_form' not in context:
            context['event_form'] = StaffAreaForm(
                    instance=self.staff_area)
        if validate_perms(request,
                          ('Volunteer Coordinator',), require=False):
            volunteer_initial_info = {
                'max_volunteer': self.staff_area.default_volunteers,
                'location': self.staff_area.default_location}
            context.update(self.get_manage_opportunity_forms(
                volunteer_initial_info,
                self.manage_vol_url,
                self.conference,
                request,
                self.staff_area.pk,
                errorcontext=errorcontext,
                labels=[self.conference.conference_slug,
                        self.staff_area.slug]))
        else:
            context['start_open'] = True

        return context

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        return render(request, self.template, self.make_context(request))

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if "manage-opps" in request.path:
            return super(EditStaffAreaView,
                         self).post(request, *args, **kwargs)
        self.groundwork(request, args, kwargs)
        context = {}
        context['event_form'] = StaffAreaForm(request.POST,
                                              instance=self.staff_area)

        if context['event_form'].is_valid():
            new_event = context['event_form'].save()
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="STAFF_AREA_UPDATE_SUCCESS",
                defaults={
                    'summary': "Staff Area has been updated",
                    'description': "Staff Area has been updated."})
            messages.success(
                request,
                '%s<br>Title: %s' % (
                    user_message[0].description,
                    new_event.title))
            if request.POST.get('edit_event', 0) != "Save and Continue":
                return HttpResponseRedirect(reverse(
                    'manage_event_list',
                    urlconf='gbe.scheduling.urls',
                    args=[self.conference.conference_slug]))
            else:
                return HttpResponseRedirect(
                    "%s?volunteer_open=True" % self.success_url)
        else:
            context['start_open'] = True
        return render(request,
                      self.template,
                      self.make_context(request, errorcontext=context))
