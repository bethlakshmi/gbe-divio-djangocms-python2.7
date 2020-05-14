from django.template import (
    loader,
    Context,
)
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import (
    CharField,
    OneToOneField,
    TextField,
)
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from gbe.models import (
    AvailableInterest,
    Conference,
)
from scheduler.models import WorkerItem
from scheduler.idd import get_roles
from gbetext import (
    best_time_to_call_options,
    phone_number_format_error,
    profile_alerts,
    states_options,
)
from gbetext import not_scheduled_roles


phone_regex = '(\d{3}[-\.]?\d{3}[-\.]?\d{4})'


class Profile(WorkerItem):
    '''
    The core data about any registered user of the GBE site, barring
    the information gathered up in the User object. (which we'll
    expose with properties, I suppose)
    '''
    user_object = OneToOneField(User)
    display_name = CharField(max_length=128, blank=True)

    # used for linking tickets
    purchase_email = CharField(max_length=64, blank=True, default='')

    # contact info - I'd like to split this out to its own object
    # so we can do real validation
    # but for now, let's just take what we get

    address1 = CharField(max_length=128, blank=True)
    address2 = CharField(max_length=128, blank=True)
    city = CharField(max_length=128, blank=True)
    state = CharField(max_length=2,
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
        return self.display_name and self.phone

    def bids_to_review(self):
        reviews = []
        missing_reviews = []
        if 'Act Reviewers' in self.privilege_groups:
            from gbe.models import Act
            reviews += Act().bids_to_review.exclude(
                flexibleevaluation__evaluator=self)
        if 'Class Reviewers' in self.privilege_groups:
            from gbe.models import Class
            reviews += Class().bids_to_review.exclude(
                bidevaluation__evaluator=self)
        if 'Costume Reviewers' in self.privilege_groups:
            from gbe.models import Costume
            reviews += Costume().bids_to_review.exclude(
                bidevaluation__evaluator=self)
        if 'Vendor Reviewers' in self.privilege_groups:
            from gbe.models import Vendor  # late import, circularity
            reviews += Vendor().bids_to_review.exclude(
                bidevaluation__evaluator=self)
        if 'Volunteer Reviewers' in self.privilege_groups:
            from gbe.models import Volunteer
            reviews += Volunteer().bids_to_review.exclude(
                bidevaluation__evaluator=self)
        return reviews

    @property
    def is_active(self):
        return self.user_object.is_active

    @property
    def contact_email(self):
        return self.user_object.email

    @property
    def address(self):
        address_string = str(self.address1.strip() +
                             '\n' +
                             self.address2.strip()).strip()
        if len(address_string) == 0:
            return ''
        if (len(self.city) == 0 or
                len(self.country) == 0 or
                len(self.state) == 0 or
                len(self.zip_code) == 0):
            return ''
        return address_string + '\n' + ' '.join((self.city + ',',
                                                 self.state,
                                                 self.zip_code,
                                                 self.country))

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

    def alerts(self, historical=False):
        if historical:
            return []
        p_alerts = []
        if (len(self.display_name.strip()) == 0 or
                len(self.purchase_email.strip()) == 0):
            p_alerts.append(profile_alerts['empty_profile'] %
                            reverse('profile_update',
                                    urlconf='gbe.urls'))
        expo_commitments = []
        expo_commitments += self.get_shows()
        expo_commitments += self.is_teaching()
        if (len(expo_commitments) > 0 and len(self.phone.strip()) == 0):
            p_alerts.append(profile_alerts['onsite_phone'] %
                            reverse('profile_update',
                                    urlconf='gbe.urls'))
        for act in self.get_acts():
            if act.accepted == 3 and \
               act.is_current and \
               (len(act.get_scheduled_rehearsals()) == 0 or
                    not act.tech.is_complete):
                p_alerts.append(
                    profile_alerts['schedule_rehearsal'] %
                    (act.b_title,
                     reverse('act_tech_wizard',
                             urlconf='gbe.urls',
                             args=[act.id])))
        return p_alerts

    def get_costumebids(self, historical=False):
        costumes = self.costumes.all()
        return (c for c in costumes if c.is_current != historical)

    def get_volunteerbids(self):
        return [vbid for vbid in self.volunteering.all() if vbid.is_current]

    def check_vol_bid(self, conference):
        from gbe.models import (
            Volunteer,
            VolunteerInterest,
        )
        if not self.volunteering.all().filter(b_conference=conference):
            volunteer = Volunteer(
                profile=self,
                number_shifts=10,
                availability="",
                unavailability="",
                opt_outs="",
                background="This was auto-generated by GBE",
                submitted=True,
                accepted=3,
                b_conference=conference,
                b_title="volunteer bid: %s" % self.get_badge_name()
            )
            volunteer.save()
            for interest in AvailableInterest.objects.filter(visible=True):
                vol_interest = VolunteerInterest(
                    interest=interest,
                    volunteer=volunteer,
                    rank=3
                )
                vol_interest.save()
        else:
            volunteer = self.volunteering.all().filter(
                b_conference=conference).first()
            volunteer.submitted = True
            volunteer.accepted = 3
            volunteer.save()

    def get_performers(self):
        performers = self.get_personae()
        performers += self.get_troupes()
        return performers

    def get_personae(self):
        solos = self.personae.all()
        performers = list(solos)
        return performers

    def get_troupes(self):
        from gbe.models import Troupe  # late import, circularity
        solos = self.personae.all()
        performers = list()
        for solo in solos:
            performers += solo.troupes.all()
        performers += Troupe.objects.filter(contact=self)
        perf_set = set(performers)
        return perf_set

    def get_acts(self, show_historical=False):
        acts = []
        performers = self.get_performers()
        for performer in performers:
            acts += performer.acts.all()
        if show_historical:
            f = lambda a: not a.is_current
        else:
            f = lambda a: a.is_current
        return list(filter(f, acts))

    def get_shows(self):
        from gbe.models import Show  # late import, circularity
        acts = self.get_acts()
        shows = []
        for act in acts:
            if act.accepted == 3 and act.is_current:
                for show in Show.objects.filter(
                        scheduler_events__resources_allocated__resource__actresource___item=act
                        ):
                    shows += [(show, act)]
        shows = sorted(shows, key=lambda show: show[0].e_title)
        return shows

    # DEPRECATE or refactor
    def get_schedule(self, conference=None):
        '''
        Gets all schedule items for a conference, if a conference is provided
        Otherwise, it's the same logic as schedule() below.
        '''
        events = self.schedule
        if conference:
            conf_events = [x for x in events if x.eventitem.get_conference() == conference]
        else:
            conf_events = events
        return conf_events

    # DEPRECATE
    @property
    def schedule(self):
        '''
        Gets all of a person's schedule.  Every way the actual human could be
        committed:
        - via profile
        - via performer(s)
        - via performing in acts
        Returns schedule as a list of Scheduler.Events
        NOTE:  Things that haven't been booked with start times won't be here.
        '''
        from scheduler.models import Event as sEvent
        acts = self.get_acts()
        events = sum([list(sEvent.objects.filter(
            resources_allocated__resource__actresource___item=act))
            for act in acts if act.accepted == 3], [])
        for performer in self.get_performers():
            events += [e for e in sEvent.objects.filter(
                resources_allocated__resource__worker___item=performer)]
        events += [e for e in sEvent.objects.filter(
            resources_allocated__resource__worker___item=self).exclude(
            resources_allocated__resource__worker__role__in=not_scheduled_roles)]
        return sorted(set(events), key=lambda event: event.start_time)

    # DEPRECATE, yes it's new.  Deprecate anyway, this hack gets through
    # GBE2018 safely.  Used by get_schedule IDD call.  Treat as private
    # and log any additional use here.
    def get_bookable_items(self):
        return {
            "acts": [act for act in self.get_acts() if act.accepted == 3],
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

    def get_badge_name(self):
        badge_name = self.display_name
        if len(badge_name) == 0:
            badge_name = self.user_object.first_name
        return badge_name

    def is_teaching(self, historical=False):
        '''
        return a list of classes this user is teaching
        '''
        if historical:
            return [c for c in self.workeritem.get_bookings('Teacher')
                    if not c.is_current]
        else:
            return [c for c in self.workeritem.get_bookings('Teacher')
                    if c.is_current]

    def vendors(self, historical=False):
        from gbe.models import Vendor  # late import, circularity
        vendors = Vendor.objects.filter(profile=self)
        if historical:
            f = lambda v: not v.is_current
        else:
            f = lambda v: v.is_current
        return list(filter(f, vendors))

    def proposed_classes(self, historical=False):
        classes = sum([list(teacher.is_teaching.all())
                       for teacher in self.personae.all()], [])
        if historical:
            f = lambda c: not c.is_current
        else:
            f = lambda c: c.is_current
        classes = list(filter(f, classes))
        return classes

    def has_role_in_event(self, role, event):
        '''
        Returns True if this person has the
        given role in the given event
        '''
        doing_it = False
        if role == "Performer":
            for show, act in self.get_shows():
                if show.pk == event.pk:
                    doing_it = True
        elif not doing_it:
            performers = self.get_performers()
            for person in event.roles([role]):
                if self.pk == person._item.pk:
                    doing_it = True
                else:
                    for perf in performers:
                        if perf.pk == person._item.pk:
                            doing_it = True
        return doing_it

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

    def __str__(self):
        return self.display_name

    @property
    def describe(self):
        return self.display_name

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['display_name']
        app_label = "gbe"
