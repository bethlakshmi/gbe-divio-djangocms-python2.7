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
from scheduler.models import WorkerItem
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


class Account(Model):
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
        from gbe.models import Biddable
        reviews = []
        reviewer = False
        priv_grps = self.privilege_groups
        for priv in ['Act Reviewers',
                     'Class Reviewers',
                     'Costume Reviewers',
                     'Vendor Reviewers']:
            if priv in priv_grps:
                reviewer = True
        if reviewer:
            bids_to_review = Biddable.objects.filter(
                b_conference__status__in=('upcoming', 'ongoing'),
                submitted=True,
                accepted=0).exclude(
                bidevaluation__evaluator=self).exclude(
                flexibleevaluation__evaluator=self).select_subclasses()
            for bid in bids_to_review:
                if "%s Reviewers" % bid.__class__.__name__ in priv_grps:
                    reviews += [bid]
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

    def alerts(self, shows, classes):
        p_alerts = []

        if (len(self.display_name.strip()) == 0 or
                len(self.purchase_email.strip()) == 0):
            p_alerts.append(profile_alerts['empty_profile'] %
                            reverse('profile_update',
                                    urlconf='gbe.urls'))
        for show, act in shows:
            if act.accepted == 3 and act.profile == self and not (
                    act.is_complete):
                p_alerts.append(
                    profile_alerts['schedule_rehearsal'] %
                    (act.b_title, reverse('act_tech_wizard',
                                          urlconf='gbe.urls',
                                          args=[act.id])))
        return p_alerts

    def get_costumebids(self, historical=False):
        if historical:
            return self.costumes.filter(b_conference__status="completed")
        else:
            return self.costumes.exclude(b_conference__status="completed")

    def get_performers(self, organize=False):
        from gbe.models import Troupe  # late import, circularity
        solos = self.personae.all()
        troupes = Troupe.objects.filter(
            Q(contact=self) | Q(membership__performer_profile=self)).distinct()
        if organize:
            return solos, troupes
        else:
            performers = list(solos)
            performers += troupes
            return performers

    def get_acts(self):
        acts = []
        performers = self.get_performers()
        for performer in performers:
            acts += performer.acts.exclude(b_conference__status="completed")
        return acts

    # DEPRECATE, yes it's new.  Deprecate anyway, this hack gets through
    # GBE2018 safely.  Used by get_schedule IDD call.  Treat as private
    # and log any additional use here.
    def get_bookable_items(self):
        return {
            "performers": self.get_performers(),
        }

    def volunteer_schedule(self, conference=None):
        conference = conference or Conference.current_conf()
        return self.workeritem.get_bookings(role="Volunteer",
                                            conference=conference).order_by(
                                                'starttime')

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
        classes = Class.objects.filter(teacher__contact=self)
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
        active_performer = Act.objects.filter(performer__contact=self).exclude(
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

    @property
    def describe(self):
        return self.display_name

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['display_name']
        app_label = "gbe"
