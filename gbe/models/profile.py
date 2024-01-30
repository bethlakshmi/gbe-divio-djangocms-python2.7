from django.template import (
    loader,
    Context,
)
from django.urls import reverse
from django.conf import settings
from django.db.models import (
    CASCADE,
    CharField,
    Model,
    OneToOneField,
    TextField,
)
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.db.models import Q
from gbe.models import Conference
from scheduler.idd import (
    get_roles,
    get_schedule,
)
from gbetext import (
    best_time_to_call_options,
    not_scheduled_roles,
    phone_number_format_error,
    privileged_event_roles,
    profile_alerts,
    role_options,
    states_options,
)


phone_regex = '(\d{3}[-\.]?\d{3}[-\.]?\d{4})'


class Profile(Model):
    '''
    The core data about any registered user of the GBE site, barring
    the information gathered up in the User object. (which we'll
    expose with properties, I suppose)
    '''
    user_object = OneToOneField(User, on_delete=CASCADE)
    display_name = CharField(max_length=128, blank=True)

    # used for linking tickets
    purchase_email = CharField(max_length=64, blank=True, default='')
    # address removed from view
    address1 = CharField(max_length=128, blank=True)
    address2 = CharField(max_length=128, blank=True)
    city = CharField(max_length=128, blank=True)
    state = CharField(max_length=5,
                      choices=states_options,
                      blank=True)
    zip_code = CharField(max_length=10, blank=True)  # allow for ext ZIP
    country = CharField(max_length=128, blank=True)
    # must have = a way to contact teachers & performers on site
    # want to have = any other primary phone that may be preferred offsite
    phone = CharField(max_length=50,
                      validators=[RegexValidator(
                          regex=phone_regex,
                          message=phone_number_format_error)])
    best_time = CharField(max_length=50,
                          choices=best_time_to_call_options,
                          default='Any',
                          blank=True)
    how_heard = TextField(blank=True)

    @property
    def how_heard_list(self):
        if self.how_heard:
            return eval(self.how_heard)
        else:
            return "None"

    @property
    def complete(self):
        return self.display_name

    @property
    def participation_ready(self):
        return self.display_name and self.phone and (
            self.user_object.first_name) and (self.user_object.last_name)

    def bids_to_review(self):
        from gbe.models import Act, Class, Costume, Vendor
        accessible_bids = []
        reviews = []
        priv_grps = self.privilege_groups
        if 'Act Reviewers' in priv_grps:
            accessible_bids += [Act]
        if 'Class Reviewers' in priv_grps:
            accessible_bids += [Class]
        if 'Costume Reviewers' in priv_grps:
            accessible_bids += [Costume]
        if 'Vendor Reviewers' in priv_grps:
            accessible_bids += [Vendor]

        if len(accessible_bids) > 0:
            for bid_class in accessible_bids:
                bid_base = bid_class.objects.filter(
                    b_conference__status__in=('upcoming', 'ongoing'),
                    submitted=True,
                    accepted=0)
                reviews += [{
                    'bid_type': bid_class.__name__,
                    'url': reverse(bid_class.__name__.lower() + '_review_list',
                                   urlconf='gbe.urls'),
                    'total_bids': bid_base.count(),
                    'unreviewed_bids': bid_base.exclude(
                        bidevaluation__evaluator=self).exclude(
                        flexibleevaluation__evaluator=self).count()}]
        return reviews

    @property
    def is_active(self):
        return self.user_object.is_active

    @property
    def contact_email(self):
        return self.user_object.email

    @property
    def address(self):
        return ' '.join(
            (self.city + ',', self.state, self.zip_code, self.country))

    @property
    def privilege_groups(self):
        groups = [group.name for
                  group in self.user_object.groups.all().order_by('name')]
        return groups

    def get_email_privs(self):
        email_privs = []
        for group in self.privilege_groups:
            if "Coordinator" in group:
                bid_type = group.split()[0]
                email_privs += [bid_type.lower()]
        return email_privs

    def alerts(self, conference, user_schedule):
        from gbe.models import Act
        from gbe.ticketing_idd_interface import get_unsigned_forms
        p_alerts = []
        if (len(self.display_name.strip()) == 0 or
                len(self.purchase_email.strip()) == 0):
            p_alerts.append(profile_alerts['empty_profile'] %
                            reverse('profile_update',
                                    urlconf='gbe.urls'))
        for act in Act.objects.filter(bio__contact=self, accepted=3).exclude(
                b_conference__status="completed"):
            if not act.is_complete:
                p_alerts.append(
                    profile_alerts['schedule_rehearsal'] %
                    (act.b_title, reverse('act_tech_wizard',
                                          urlconf='gbe.urls',
                                          args=[act.id])))
        forms_to_sign = get_unsigned_forms(self, conference, user_schedule)
        if len(forms_to_sign) > 0:
            p_alerts.append(profile_alerts['sign_form'] % reverse(
                'sign_forms',
                urlconf='ticketing.urls'))
        return p_alerts

    def get_costumebids(self, historical=False):
        if historical:
            return self.costumes.filter(b_conference__status="completed")
        else:
            return self.costumes.exclude(b_conference__status="completed")

    def volunteer_schedule(self, conference=None):
        conference = conference or Conference.current_conf()
        occurrences = []
        response = get_schedule(self.user_object,
                                labels=[conference.conference_slug],
                                roles=["Volunteer"])
        for item in response.schedule_items:
            occurrences += [item.event]
        return occurrences

    def get_roles(self, conference=None):
        '''
        Gets all of a person's roles for a conference
        '''
        roles = []
        if conference is None:
            roles = get_roles(
                self.user_object,
                labels=Conference.objects.exclude(
                    status="completed").values_list(
                    'conference_slug',
                    flat=True)).roles
            if "Staff Lead" not in roles and self.staffarea_set.exclude(
                    conference__status="completed").exists():
                roles += ["Staff Lead"]
        else:
            roles = get_roles(self.user_object,
                              labels=[conference.conference_slug]).roles
            if "Staff Lead" not in roles and self.staffarea_set.filter(
                    conference=conference).exists():
                roles += ["Staff Lead"]
        return roles

    def get_priv_roles(self, conference=None):
        '''
        Gets only roles that have special privileges
        '''
        roles = self.get_roles(conference)
        return [perm for perm in privileged_event_roles if perm in roles]

    def get_badge_name(self):
        badge_name = self.display_name
        if len(badge_name) == 0:
            badge_name = self.user_object.first_name
        return badge_name

    def vendors(self, historical=False):
        from gbe.models import Vendor  # late import, circularity
        vendors = Vendor.objects.filter(business__owners=self)
        if historical:
            vendors = vendors.filter(b_conference__status="completed")
        else:
            vendors = vendors.exclude(b_conference__status="completed")
        return vendors

    def proposed_classes(self, historical=False):
        from gbe.models import Class
        classes = Class.objects.filter(teacher_bio__contact=self)
        if historical:
            classes = classes.filter(b_conference__status="completed")
        else:
            classes = classes.exclude(b_conference__status="completed")
        return classes

    def email_allowed(self, email_type):
        from gbe.models import ProfilePreferences
        if not self.user_object.is_active:
            return False
        else:
            try:
                method_name = 'send_'+str(email_type)
                method = getattr(self.preferences,
                                 method_name,
                                 lambda: 'Invalid')
                return method
            except ProfilePreferences.DoesNotExist:
                pref = ProfilePreferences(profile=self)
                pref.save()
        return True

    def currently_involved(self):
        from gbe.models import Act

        active_vendor = self.vendors().exclude(accepted__in=(1, 4, 5)).exists()
        active_teacher = self.proposed_classes().exclude(
            accepted__in=(1, 4, 5)).exists()
        active_performer = Act.objects.filter(bio__contact=self).exclude(
            b_conference__status="completed", accepted__in=(1, 4, 5)).exists()
        active_costuming = self.costumes.exclude(
            accepted__in=(1, 4, 5)).exists()
        bid_evaluator = self.bidevaluation_set.exclude(
            bid__accepted__in=(1, 4, 5),
            bid__b_conference__status="completed").exists()
        act_evaluator = self.actbidevaluation_set.exclude(
            bid__accepted__in=(1, 4, 5),
            bid__b_conference__status="completed").exists()

        if active_teacher or active_performer or active_vendor or (
                active_costuming) or bid_evaluator or act_evaluator:
            return True

        # separated for performance if the queries above show anything,
        # this never gets executed
        current = Conference.current_conf()
        if current is not None:
            all_roles = []
            for n, m in role_options:
                if m not in ("Interested", "Rejected"):
                    all_roles += [m]
            volunteer_sched = get_schedule(
                user=self.user_object,
                labels=["Volunteer", current.conference_slug],
                roles=all_roles)
            if len(volunteer_sched.schedule_items) > 0:
                return True

        return False

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['display_name']
        app_label = "gbe"
