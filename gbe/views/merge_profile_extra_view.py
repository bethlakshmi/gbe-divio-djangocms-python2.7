from django.views.generic import FormView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from gbe_utils.mixins import (
    GbeContextMixin,
    RoleRequiredMixin,
)
from gbe.models import (
    Act,
    ActBidEvaluation,
    Article,
    BidEvaluation,
    Bio,
    Business,
    Class,
    Costume,
    FlexibleEvaluation,
    Profile,
    StaffArea,
    UserMessage,
    Vendor,
    VolunteerEvaluation,
)
from ticketing.models import Purchaser
from gbe.forms import BidBioMergeForm
from gbetext import (
    merge_bio_msg,
    warn_user_merge_delete_2,
)
from scheduler.idd import (
    get_bookable_people,
    get_bookable_people_by_user,
    get_schedule,
    port_eval_info,
    reschedule,
    update_bookable_people,
)
from gbe.scheduling.views.functions import show_general_status
from settings import GBE_DATETIME_FORMAT


class MergeProfileExtra(GbeContextMixin, RoleRequiredMixin, FormView):
    # this view consciously discards old Volunteer bids, since they
    # should eventually age out of the system.
    success_url = reverse_lazy("manage_users", urlconf="gbe.urls")
    form_class = BidBioMergeForm
    view_permissions = ('Registrar', )
    intro_text = merge_bio_msg
    page_title = 'Merge Users - Merge Bios'
    view_title = 'Merge Users - Merge Bios'
    template_name = 'gbe/bid_bio_merge.tmpl'

    def has_permission(self):
        permitted = super().has_permission()
        if permitted and self.request.user.profile.pk == int(
                self.kwargs['from_pk']):
            permitted = False
            error = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SELF_MERGE_ERROR",
                defaults={
                    'summary': "Error on self-delete attempt",
                    'description': warn_user_merge_delete_2})[0].description
            messages.error(self.request, error)
        return permitted

    def get_initial(self):
        self.otherprofile = get_object_or_404(Profile,
                                              pk=self.kwargs['from_pk'])
        self.targetprofile = get_object_or_404(Profile,
                                               pk=self.kwargs['pk'])

        return {
            'otherprofile': self.otherprofile,
            'targetprofile': self.targetprofile,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sorting_off'] = True
        context['columns'] = ['Value',
                              'Target',
                              'To be Merged',
                              'Fix it Here']
        context['otherprofile'] = self.otherprofile
        context['targetprofile'] = self.targetprofile
        return context

    def replace_in_user_set(self, replace_people):
        users = []
        replaced = False
        for user in replace_people.users:
            # replace the user only if it's in the set
            if user.pk == self.otherprofile.user_object.pk:
                if self.targetprofile.user_object not in replace_people.users:
                    users += [self.targetprofile.user_object]
            else:
                users += [user]
        replace_object = eval(
            replace_people.public_class).objects.get(
            pk=replace_people.public_id)
        response = update_bookable_people(replace_object, users)
        show_general_status(self.request,
                            response,
                            self.__class__.__name__)

    def form_valid(self, form):
        form_response = super().form_valid(form)
        for bio in self.otherprofile.bio_set.all():
            if form.cleaned_data['bio_%d' % bio.pk] == '':
                bio.contact = self.targetprofile
                bio.save()
                response = get_bookable_people(bio.pk, bio.__class__.__name__)
                for bio in response.people:
                    self.replace_in_user_set(bio)
            else:
                target_bio = form.cleaned_data['bio_%d' % bio.pk]
                Act.objects.filter(bio=bio).update(bio=target_bio)
                Class.objects.filter(teacher_bio=bio).update(
                    teacher_bio=target_bio)
                Costume.objects.filter(bio=bio).update(bio=target_bio)
                response = reschedule(
                    bio.__class__.__name__,
                    bio.pk,
                    "Bio",
                    target_bio,
                    new_users=[self.targetprofile.user_object])
                show_general_status(self.request,
                                    response,
                                    self.__class__.__name__)

        Costume.objects.filter(profile=self.otherprofile).update(
            profile=self.targetprofile)

        for biz in self.otherprofile.business_set.all():
            if form.cleaned_data['business_%d' % biz.pk] == '':
                biz.owners.add(self.targetprofile)
                biz.owners.remove(self.otherprofile)
            else:
                target_biz = get_object_or_404(
                    Business,
                    pk=int(form.cleaned_data['business_%d' % biz.pk]))
                Vendor.objects.filter(business=biz).update(
                    business=target_biz)
                if biz.owners.count() == 1:
                    messages.success(
                        self.request,
                        "Sucessfully deleted business %s for profile %s." % (
                            biz.name,
                            self.otherprofile.get_badge_name()))
                    biz.delete()
                else:
                    biz.owners.remove(self.otherprofile)

        StaffArea.objects.filter(staff_lead=self.otherprofile).update(
            staff_lead=self.targetprofile)
        for group in self.otherprofile.user_object.groups.all():
            if not self.targetprofile.user_object.groups.filter(id=group.id):
                group.user_set.add(self.targetprofile.user_object)

        # change all profile scheduling items to new profile
        response = reschedule(self.otherprofile.__class__.__name__,
                              self.otherprofile.pk,
                              self.targetprofile.__class__.__name__,
                              self.targetprofile.pk,
                              [self.targetprofile.user_object])
        show_general_status(self.request,
                            response,
                            self.__class__.__name__)

        ActBidEvaluation.objects.filter(
            evaluator__pk=self.otherprofile.pk).update(
            evaluator=self.targetprofile)
        for evaluation in FlexibleEvaluation.objects.filter(
                evaluator__pk=self.otherprofile.pk):
            if not FlexibleEvaluation.objects.filter(
                    evaluator__pk=self.targetprofile.pk,
                    bid=evaluation.bid,
                    category=evaluation.category).exists():
                evaluation.evaluator = self.targetprofile
                evaluation.save()
        BidEvaluation.objects.filter(
            evaluator__pk=self.otherprofile.pk).update(
            evaluator=self.targetprofile)
        Article.objects.filter(creator__pk=self.otherprofile.pk).update(
            creator=self.targetprofile)
        Purchaser.objects.filter(
            matched_to_user=self.otherprofile.user_object).update(
            matched_to_user=self.targetprofile.user_object)
        port_eval_info(self.otherprofile.user_object,
                       self.targetprofile.user_object)

        # get any troupe memberships (not owner) - and replace user
        response = get_bookable_people_by_user(self.otherprofile.user_object)
        for people in response.people:
            self.replace_in_user_set(people)

        # do a check - user should only be in unported bios, and should NOT
        # be scheduled for anything at the end.
        response = get_schedule(user=self.otherprofile.user_object)
        for item in response.schedule_items:
            event_desc = item.event.title + " - " + \
                item.event.starttime.strftime(GBE_DATETIME_FORMAT)
            for slug in item.event.labels:
                event_desc = event_desc + " - " + slug
            messages.error(
                self.request,
                "Error - the merged profile is still booked for %s" % (
                    event_desc))
        if not response.schedule_items:
            for bio in self.otherprofile.bio_set.all():
                messages.success(
                    self.request,
                    "Sucessfully deleted bio %s for profile %s." % (
                        bio.name,
                        self.otherprofile.get_badge_name()))
                bio.delete()
            messages.success(
                self.request,
                "Sucessfully deleted profile %s." % (
                        self.otherprofile.get_badge_name()))
            self.otherprofile.user_object.delete()
        else:
            messages.error(
                self.request,
                "Skipped deletion because of errors above.  Contact the admin")
        return form_response
