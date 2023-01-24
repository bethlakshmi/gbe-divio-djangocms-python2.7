from django.contrib.auth.models import User
from post_office.models import EmailTemplate
from factory import (
    post_generation,
    LazyAttribute,
    RelatedFactory,
    SelfAttribute,
    Sequence,
    SubFactory,
)
from factory.django import (
    DjangoModelFactory,
    ImageField,
)
import gbe.models as conf
from django.contrib.auth.models import User
import scheduler.models as sched
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from pytz import utc
from cms.models.permissionmodels import PageUser


class ConferenceFactory(DjangoModelFactory):
    class Meta:
        model = conf.Conference

    conference_name = Sequence(lambda n: "Test Conference %d" % n)
    conference_slug = Sequence(lambda n: "test_conf_%d" % n)
    accepting_bids = False
    status = 'upcoming'


class ConferenceDayFactory(DjangoModelFactory):
    day = date.today() + timedelta(7)
    conference = SubFactory(ConferenceFactory)

    class Meta:
        model = conf.ConferenceDay


class WorkerItemFactory(DjangoModelFactory):
    class Meta:
        model = sched.WorkerItem


class UserFactory(DjangoModelFactory):
    ''' the created_by_id of a Page User is a hack to get to python 3.8,
    Django CMS > 3.7.  If this is ever really fixed, it can be removed:
    https://github.com/django-cms/django-cms/issues/7225 '''
    class Meta:
        model = PageUser
    id = Sequence(lambda n: n)
    email = Sequence(lambda n: 'John_%s@smith.com' % str(n))
    username = LazyAttribute(lambda a: "%s" % (a.email))
    created_by_id = LazyAttribute(lambda a: a.id)


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = conf.Profile
    user_object = SubFactory(UserFactory)
    city = 'Smithville'
    state = 'MD'
    zip_code = '12345'
    country = 'USA'
    display_name = Sequence(lambda n: "%s_%s" % (str(n), str(n)))


class PersonaFactory(DjangoModelFactory):
    class Meta:
        model = conf.Persona
    contact = SubFactory(ProfileFactory)
    performer_profile = LazyAttribute(lambda a: a.contact)
    name = Sequence(lambda n: 'Test Persona %d' % n)
    year_started = 2004


class TroupeFactory(DjangoModelFactory):
    class Meta:
        model = conf.Troupe
    contact = SubFactory(ProfileFactory)
    name = Sequence(lambda n: 'Test Troupe %d' % n)
    year_started = 2004


class SocialLinkFactory(DjangoModelFactory):
    class Meta:
        model = conf.SocialLink
    performer = SubFactory(PersonaFactory)
    social_network = 'Website'
    link = Sequence(lambda n: '"http://www.foo%d.com"' % n)
    order = 1


class TechInfoFactory(DjangoModelFactory):
    class Meta:
        model = conf.TechInfo

    track_title = Sequence(lambda n: 'Test Track Title %d' % n)
    track_artist = Sequence(lambda n: 'Test Track Artist %d' % n)
    duration = timedelta(minutes=5)


class ActCastingOptionFactory(DjangoModelFactory):
    class Meta:
        model = conf.ActCastingOption
    casting = "Hosted by..."
    display_header = "Hostest with the mostest"
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


class ClassFactory(DjangoModelFactory):
    class Meta:
        model = conf.Class
    b_title = Sequence(lambda x: "Test Class #%d" % x)
    b_description = LazyAttribute(
        lambda a: "Description for %s" % a.b_title)
    submitted = False
    teacher = SubFactory(PersonaFactory)
    minimum_enrollment = 1
    maximum_enrollment = 20
    organization = "Some Organization"
    type = "Lecture"
    fee = 0
    length_minutes = 60
    history = LazyAttribute(
        lambda a: "History for test Class %s" % a.b_title)
    run_before = LazyAttribute(
        lambda a:
        "run_before for test Class %s" % a.b_title)
    schedule_constraints = "[]"
    space_needs = ''
    physical_restrictions = LazyAttribute(
        lambda a: "physical restrictions for test Class %s" % a.b_title)
    multiple_run = 'No'
    b_conference = SubFactory(ConferenceFactory)


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
    b_conference = SubFactory(ConferenceFactory)


class BusinessFactory(DjangoModelFactory):
    class Meta:
        model = conf.Business

    name = Sequence(lambda x: "Business # %d" % x)
    website = "http://www.foo.com"
    physical_address = "123 Main Street"
    publish_physical_address = False
    description = Sequence(lambda x: "Business Description # %d" % x)

    @post_generation
    def owners(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # A list of groups were passed in, use them
            for owner in extracted:
                self.owners.add(owner)
        else:
            self.owners.add(ProfileFactory())


class VendorFactory(DjangoModelFactory):
    class Meta:
        model = conf.Vendor
    business = SubFactory(BusinessFactory)
    b_title = "DON'T USE"
    want_help = False
    help_description = LazyAttribute(
        lambda a: "Help description for Test Business #%s" %
        a.business.name)
    help_times = "[u'VSH0', u'VSH2']"

    b_conference = SubFactory(ConferenceFactory)


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
    picture = ImageField(filename="file.jpg")


class ConferenceDayFactory(DjangoModelFactory):
    class Meta:
        model = conf.ConferenceDay
    conference = SubFactory(ConferenceFactory)
    day = date(2016, 2, 5)


class UserMessageFactory(DjangoModelFactory):
    class Meta:
        model = conf.UserMessage
    view = Sequence(lambda x: "View%d" % x)
    code = Sequence(lambda x: "CODE_%d" % x)
    summary = Sequence(lambda x: "Message Summary #%d" % x)
    description = Sequence(lambda x: "Description #%d" % x)


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


class EmailFrequencyFactory(DjangoModelFactory):
    email_type = "act_tech_reminder"
    weekday = datetime.now().weekday()

    class Meta:
        model = conf.EmailFrequency


class StaffAreaFactory(DjangoModelFactory):
    title = Sequence(lambda x: "Staff Title #%d" % x)
    slug = Sequence(lambda x: "slug_%d" % x)
    conference = SubFactory(ConferenceFactory)
    description = Sequence(lambda x: "description #%d" % x)

    class Meta:
        model = conf.StaffArea


class StyleVersionFactory(DjangoModelFactory):
    class Meta:
        model = conf.StyleVersion
    name = Sequence(lambda n: 'Style Version %d' % n)
    number = 1.0


class StyleSelectorFactory(DjangoModelFactory):
    class Meta:
        model = conf.StyleSelector
    selector = Sequence(lambda n: 'style_selector_%d' % n)
    used_for = "General"


class StylePropertyFactory(DjangoModelFactory):
    class Meta:
        model = conf.StyleProperty
    selector = SubFactory(StyleSelectorFactory)
    style_property = Sequence(lambda n: 'style_property_%d' % n)
    value_type = "rgba"
    value_template = "{}"


class StyleGroupFactory(DjangoModelFactory):
    class Meta:
        model = conf.StyleGroup
    name = Sequence(lambda n: 'Group Name %d' % n)
    test_notes = Sequence(lambda n: 'label help text%d' % n)
    order = Sequence(lambda n: n)


class StyleLabelFactory(DjangoModelFactory):
    class Meta:
        model = conf.StyleLabel
    group = SubFactory(StyleGroupFactory)
    name = Sequence(lambda n: 'Label Name %d' % n)
    help_text = Sequence(lambda n: 'label help text %d' % n)
    order = Sequence(lambda n: n)


class StyleElementFactory(DjangoModelFactory):
    class Meta:
        model = conf.StyleElement
    group = SubFactory(StyleGroupFactory)
    name = Sequence(lambda n: 'Element Name %d' % n)
    description = Sequence(lambda n: 'Description %d' % n)
    order = Sequence(lambda n: n)
    sample_html = Sequence(lambda n: '<a>%d</a>' % n)


class StyleValueFactory(DjangoModelFactory):
    class Meta:
        model = conf.StyleValue
    style_property = SubFactory(StylePropertyFactory)
    style_version = SubFactory(StyleVersionFactory)
    value = "rgba(1,1,1,0)"
    parseable_values = "rgba(1,1,1,0)"


class StyleValueImageFactory(DjangoModelFactory):
    class Meta:
        model = conf.StyleValue
    style_property = SubFactory(StylePropertyFactory, value_type="image")
    style_version = SubFactory(StyleVersionFactory)
    value = ""


class TestURLFactory(DjangoModelFactory):
    class Meta:
        model = conf.TestURL
    display_name = Sequence(lambda n: 'Element Name %d' % n)
    partial_url = Sequence(lambda n: '/gbe/%d' % n)
    test_notes = "notes"


class UserStylePreviewFactory(DjangoModelFactory):
    class Meta:
        model = conf.UserStylePreview
    version = SubFactory(StyleVersionFactory)
    previewer = SubFactory(UserFactory)
