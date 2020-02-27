from django.contrib.auth.models import User
from post_office.models import EmailTemplate
from factory import (
    Sequence,
    DjangoModelFactory,
    SubFactory,
    RelatedFactory,
    LazyAttribute,
    SelfAttribute
)
import gbe.models as conf
from django.contrib.auth.models import User
import scheduler.models as sched
from gbe.duration import Duration
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import (
    date,
    time,
    timedelta,
)
from pytz import utc


class AvailableInterestFactory(DjangoModelFactory):
    class Meta:
        model = conf.AvailableInterest
        django_get_or_create = ('interest',)
    interest = 'Registration'


class ConferenceFactory(DjangoModelFactory):
    class Meta:
        model = conf.Conference

    conference_name = Sequence(lambda n: "Test Conference %d" % n)
    conference_slug = Sequence(lambda n: u"test_conf_%d" % n)
    accepting_bids = False
    status = 'upcoming'


class ConferenceDayFactory(DjangoModelFactory):
    day = date.today() + timedelta(7)
    conference = SubFactory(ConferenceFactory)

    class Meta:
        model = conf.ConferenceDay


class VolunteerWindowFactory(DjangoModelFactory):
    start = time(8, 0, 0)
    end = time(12, 0, 0)
    day = SubFactory(ConferenceDayFactory)

    class Meta:
        model = conf.VolunteerWindow


class WorkerItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.WorkerItem


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    first_name = Sequence(lambda n: 'John_%s' % str(n))
    last_name = 'Smith'
    username = LazyAttribute(lambda a: "%s" % (a.first_name))
    email = LazyAttribute(lambda a: '%s@smith.com' % (a.username))


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = conf.Profile
    user_object = SubFactory(UserFactory)
    address1 = '123 Main St.'
    address2 = Sequence(lambda n: 'Apt. %d' % n)
    city = 'Smithville'
    state = 'MD'
    zip_code = '12345'
    country = 'USA'
    phone = '617-282-9268'
    display_name = LazyAttribute(
        lambda a: "%s_%s" % (a.user_object.first_name,
                             a.user_object.last_name))


class ShowFactory(DjangoModelFactory):
    class Meta:
        model = conf.Show
    e_title = Sequence(lambda n: 'Test Show%d' % n)
    e_description = 'Test Description'
    duration = Duration(hours=1)
    e_conference = SubFactory(ConferenceFactory)


class PersonaFactory(DjangoModelFactory):
    class Meta:
        model = conf.Persona
    contact = SubFactory(ProfileFactory)
    performer_profile = LazyAttribute(lambda a: a.contact)
    name = Sequence(lambda n: 'Test Persona %d' % n)
    experience = 4


class TroupeFactory(DjangoModelFactory):
    class Meta:
        model = conf.Troupe
    contact = SubFactory(ProfileFactory)
    name = Sequence(lambda n: 'Test Troupe %d' % n)
    experience = 4


class ComboFactory(DjangoModelFactory):
    class Meta:
        model = conf.Combo
    contact = SubFactory(ProfileFactory)
    name = Sequence(lambda n: 'Test Combo %d' % n)
    experience = 5


class AudioInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.AudioInfo

    track_title = Sequence(lambda n: 'Test Track Title %d' % n)
    track_artist = Sequence(lambda n: 'Test Track Artist %d' % n)
#  no track for now  - do we mock this, or what?
    track_duration = Duration(minutes=5)
    need_mic = True
    own_mic = False
    notes = "Notes about test AudioInfo object."
    confirm_no_music = False


class LightingInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.LightingInfo
    notes = "Notes field for test LightingInfo object."
    costume = "Costume field for test LightingInfo object."


class TechInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.TechInfo

    audio = SubFactory(AudioInfoFactory)
    lighting = SubFactory(LightingInfoFactory)


class CueInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.CueInfo

    techinfo = SubFactory(TechInfoFactory)
    cue_sequence = Sequence(lambda n: n)
    cue_off_of = "cue_off_of field for test CueInfo object"
    follow_spot = "follow_spot"
    center_spot = "center_spot"
    backlight = "backlight"
    cyc_color = "WHITE"
    wash = "WHITE"
    sound_note = "sound_note field for test CueInfo object"


class ActCastingOptionFactory(DjangoModelFactory):
    class Meta:
        model = conf.ActCastingOption
    casting = "Hosted by..."
    display_order = 0


class ActFactory(DjangoModelFactory):
    class Meta:
        model = conf.Act

    submitted = False
    b_title = Sequence(lambda x: "Act #%d" % x)
    performer = SubFactory(PersonaFactory)
    tech = SubFactory(TechInfoFactory)
    video_link = ""
    video_choice = ""
    shows_preferences = "[]"
    why_you = "why_you field for test Act"
    b_conference = SubFactory(ConferenceFactory)


class RoomFactory(DjangoModelFactory):
    class Meta:
        model = conf.Room

    name = Sequence(lambda x: "Test Room #%d" % x)
    capacity = 40
    overbook_size = 50


class EventFactory(DjangoModelFactory):
    class Meta:
        model = conf.Event

    e_title = Sequence(lambda x: "Test Event #%d" % x)
    e_description = LazyAttribute(
        lambda a: "Description for %s" % a.e_title)
    blurb = LazyAttribute(
        lambda a: "Blurb for %s" % a.e_title)
    duration = Duration(hours=2)
    e_conference = SubFactory(ConferenceFactory)


class GenericEventFactory(DjangoModelFactory):
    class Meta:
        model = conf.GenericEvent

    e_title = Sequence(lambda n: 'Test Generic Event %d' % n)
    e_description = LazyAttribute(
        lambda a: "Description for %s" % a.e_title)
    duration = Duration(hours=1)
    type = 'Special'
    volunteer_type = SubFactory(AvailableInterestFactory)
    e_conference = SubFactory(ConferenceFactory)


class ClassFactory(DjangoModelFactory):
    class Meta:
        model = conf.Class
    e_title = Sequence(lambda x: "Test Class #%d" % x)
    e_description = LazyAttribute(
        lambda a: "Description for %s" % a.e_title)
    b_title = Sequence(lambda x: "Test Class #%d" % x)
    b_description = LazyAttribute(
        lambda a: "Description for %s" % a.e_title)

    duration = Duration(hours=1)
    teacher = SubFactory(PersonaFactory)
    minimum_enrollment = 1
    maximum_enrollment = 20
    organization = "Some Organization"
    type = "Lecture"
    fee = 0
    length_minutes = 60
    history = LazyAttribute(
        lambda a: "History for test Class %s" % a.e_title)
    run_before = LazyAttribute(
        lambda a:
        "run_before for test Class %s" % a.e_title)
    schedule_constraints = "[]"
    space_needs = ''
    physical_restrictions = LazyAttribute(
        lambda a: "physical restrictions for test Class %s" % a.e_title)
    multiple_run = 'No'
    b_conference = SubFactory(ConferenceFactory)
    e_conference = SubFactory(ConferenceFactory)


class BidEvaluationFactory(DjangoModelFactory):
    class Meta:
        model = conf.BidEvaluation

    evaluator = SubFactory(ProfileFactory)
    vote = 3
    notes = "Notes field for test BidEvaluation"
    bid = SubFactory(ActFactory)


class ActBidEvaluationFactory(DjangoModelFactory):
    class Meta:
        model = conf.ActBidEvaluation

    bid = SubFactory(ActFactory)
    evaluator = SubFactory(ProfileFactory)
    notes = LazyAttribute(
        lambda a: "Notes for Bid %s, by Evaluator %s" % (a.bid.b_title,
                                                         a.evaluator))


class VolunteerFactory(DjangoModelFactory):
    class Meta:
        model = conf.Volunteer

    profile = SubFactory(ProfileFactory)
    number_shifts = 1
    availability = LazyAttribute(
        lambda a: ("Availability for test Volunteer #%s" %
                   a.profile.display_name))
    unavailability = LazyAttribute(
        lambda a: ("Unavailability for test Volunteer #%s" %
                   a.profile.display_name))
    opt_outs = LazyAttribute(
        lambda a: ("Opt-outs for test Volunteer #%s" %
                   a.profile.display_name))
    pre_event = False
    background = LazyAttribute(
        lambda a: ("Background for test Volunteer #%s" %
                   a.profile.display_name))
    b_conference = SubFactory(ConferenceFactory)


class VolunteerInterestFactory(DjangoModelFactory):
    class Meta:
        model = conf.VolunteerInterest

    interest = SubFactory(AvailableInterestFactory, interest='Security/usher')
    volunteer = SubFactory(VolunteerFactory)
    rank = 4


class VendorFactory(DjangoModelFactory):
    class Meta:
        model = conf.Vendor

    b_title = Sequence(lambda x: "Vendor # %d" % x)
    profile = SubFactory(ProfileFactory)
    website = "http://www.foo.com"
    physical_address = "123 Main Street"
    publish_physical_address = False
    #    logo = models.FileField(upload_to="uploads/images", blank=True)
    want_help = False
    help_description = LazyAttribute(
        lambda a: "Help description for Test Volunteer #%s" %
        a.profile.display_name)
    help_times = "[u'VSH0', u'VSH2']"

    b_conference = SubFactory(ConferenceFactory)


class ClassProposalFactory(DjangoModelFactory):
    class Meta:
        model = conf.ClassProposal

    title = Sequence(lambda x: "Class Proposal %d: Title" % x)
    name = Sequence(
        lambda x: "Class Proposal %d: Name of Proposer" % x)
    email = Sequence(lambda x: "john%d@gmail.com" % x)
    proposal = LazyAttribute(lambda a: "Proposal titled %s" % a.title)
    type = 'Class'
    display = False
    conference = SubFactory(ConferenceFactory)


class ConferenceVolunteerFactory(DjangoModelFactory):
    class Meta:
        model = conf.ConferenceVolunteer

    presenter = SubFactory(PersonaFactory)
    bid = SubFactory(ClassProposalFactory)
    how_volunteer = 'Any of the Above'
    qualification = 'True'
    volunteering = True


class ProfilePreferencesFactory(DjangoModelFactory):
    class Meta:
        model = conf.ProfilePreferences

    profile = SubFactory(ProfileFactory)
    in_hotel = "No"
    inform_about = []
    show_hotel_infobox = True


class CostumeFactory(DjangoModelFactory):
    class Meta:
        model = conf.Costume
    b_title = Sequence(lambda x: "Test Costume #%d" % x)
    b_description = LazyAttribute(
        lambda a: "Description for %s" % a.b_title)

    profile = SubFactory(ProfileFactory)
    b_conference = SubFactory(ConferenceFactory)
    active_use = True
    pieces = 10
    pasties = False
    dress_size = 10
    picture = SimpleUploadedFile("file.jpg",
                                 "file_content",
                                 content_type="image/jpg")


class ConferenceDayFactory(DjangoModelFactory):
    class Meta:
        model = conf.ConferenceDay
    conference = SubFactory(ConferenceFactory)
    day = date(2016, 2, 5)


class VolunteerWindowFactory(DjangoModelFactory):
    class Meta:
        model = conf.VolunteerWindow
    day = SubFactory(ConferenceDayFactory)
    start = time(10)
    end = time(14)


class UserMessageFactory(DjangoModelFactory):
    class Meta:
        model = conf.UserMessage
    view = Sequence(lambda x: "View%d" % x)
    code = Sequence(lambda x: "CODE_%d" % x)
    summary = Sequence(lambda x: "Message Summary #%d" % x)
    description = Sequence(lambda x: "Description #%d" % x)


class ShowVoteFactory(DjangoModelFactory):
    show = SubFactory(ShowFactory)
    vote = 3

    class Meta:
        model = conf.ShowVote


class EvaluationCategoryFactory(DjangoModelFactory):
    category = Sequence(lambda x: "Category %d" % x)
    help_text = Sequence(lambda x: "Notes for Category %d" % x)

    class Meta:
        model = conf.EvaluationCategory


class FlexibleEvaluationFactory(DjangoModelFactory):
    category = SubFactory(EvaluationCategoryFactory)
    evaluator = SubFactory(ProfileFactory)
    bid = SubFactory(ActFactory)
    ranking = 3

    class Meta:
        model = conf.FlexibleEvaluation


class EmailTemplateFactory(DjangoModelFactory):
    class Meta:
        model = User
    name = Sequence(lambda n: 'Template - %d' % n)
    subject = 'Test Template Subject'
    content = "text content"
    html_content = "html text content"

    class Meta:
        model = EmailTemplate


class EmailTemplateSenderFactory(DjangoModelFactory):
    from_email = "default@sender.com"
    template = SubFactory(EmailTemplateFactory)

    class Meta:
        model = conf.EmailTemplateSender


class StaffAreaFactory(DjangoModelFactory):
    title = Sequence(lambda x: "Staff Title #%d" % x)
    slug = Sequence(lambda x: "slug_%d" % x)
    conference = SubFactory(ConferenceFactory)
    description = Sequence(lambda x: "description #%d" % x)

    class Meta:
        model = conf.StaffArea
