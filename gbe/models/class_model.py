import pytz
from itertools import chain
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    IntegerField,
    Q,
    TextField,
)
from gbe.models import (
    Biddable,
    Bio,
    Conference,
)
from gbetext import (
    acceptance_states,
    class_length_options,
    class_options,
    space_options,
    yesno_options,
)
from settings import GBE_TABLE_FORMAT


class Class(Biddable):
    '''
    A Class is an Event where one or a few people
    teach/instruct/guide/mediate and a number of participants
    spectate/participate.
    '''
    teacher_bio = ForeignKey(Bio,
                             on_delete=CASCADE,
                             related_name='is_teaching')
    minimum_enrollment = IntegerField(blank=True, default=1)
    maximum_enrollment = IntegerField(blank=True, default=20, null=True)
    organization = CharField(max_length=128, blank=True)
    type = CharField(max_length=128,
                     choices=class_options,
                     blank=True,
                     default="Lecture")
    fee = IntegerField(blank=True, default=0, null=True)
    other_teachers = CharField(max_length=128, blank=True)
    length_minutes = IntegerField(choices=class_length_options,
                                  default=60, blank=True)
    history = TextField(blank=True)
    run_before = TextField(blank=True)
    schedule_constraints = TextField(blank=True)
    avoided_constraints = TextField(blank=True)
    space_needs = CharField(max_length=128,
                            choices=space_options,
                            blank=True,
                            default='')
    physical_restrictions = TextField(blank=True)
    multiple_run = CharField(max_length=20,
                             choices=yesno_options, default="No")

    def clone(self):
        new_class = Class()
        new_class.teacher_bio = self.teacher_bio
        new_class.minimum_enrollment = self.minimum_enrollment
        new_class.organization = self.organization
        new_class.type = self.type
        new_class.fee = self.fee
        new_class.other_teachers = self.other_teachers
        new_class.length_minutes = self.length_minutes
        new_class.history = self.history
        new_class.run_before = self.run_before
        new_class.space_needs = self.space_needs
        new_class.physical_restrictions = self.physical_restrictions
        new_class.multiple_run = self.multiple_run
        new_class.b_title = self.b_title
        new_class.b_description = self.b_description
        new_class.b_conference = Conference.objects.filter(
            status="upcoming").first()

        new_class.save()
        return new_class

    @property
    def teacher(self):
        return self.teacher_bio

    @property
    def get_space_needs(self):
        needs = ""
        for top, top_opts in space_options:
            for key, sub_level in top_opts:
                if key == self.space_needs:
                    needs = top + " - " + sub_level
        return needs

    @property
    def bid_review_header(self):
        return (['Title',
                 'Teacher',
                 'Type',
                 'Last Update',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        return [self.b_title,
                self.teacher,
                self.type,
                self.updated_at.strftime(GBE_TABLE_FORMAT),
                acceptance_states[self.accepted][1]]

    @property
    def profile(self):
        return self.teacher.contact

    def __str__(self):
        return self.b_title

    class Meta:
        verbose_name_plural = 'classes'
        app_label = "gbe"
