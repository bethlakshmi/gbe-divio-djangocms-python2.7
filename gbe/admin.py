from django.contrib import admin
from gbe.models import *
from model_utils.managers import InheritanceManager
from import_export.admin import ImportExportActionModelAdmin


class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('conference_name',
                    'conference_slug',
                    'status',
                    'accepting_bids')
    list_filter = ['status', 'act_style']


@admin.register(StaffArea)
class StaffAreaAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'conference',
                    'title',
                    'staff_lead')
    list_editable = ('title',
                     'staff_lead',)
    list_display_links = ('id',)
    list_filter = ['conference__conference_slug', 'slug']


class BidAdmin(ImportExportActionModelAdmin):
    list_display = (str, 'submitted', 'accepted', 'created_at', 'updated_at')
    list_filter = ['submitted', 'accepted', 'b_conference']


class ClassAdmin(BidAdmin):
    list_display = ('__unicode__',
                    'teacher',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    list_filter = ['submitted', 'accepted', 'b_conference__conference_slug']
    search_fields = ['e_title']


class ActAdmin(admin.ModelAdmin):
    list_display = ('performer',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    list_filter = ['submitted', 'accepted', 'b_conference__conference_slug']
    search_fields = ['b_title']


class PerformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')
    search_fields = ['name']


class TroupeAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')
    filter_horizontal = ("membership",)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_object', 'phone', 'purchase_email')
    search_fields = ['display_name',
                     'user_object__email']


class AudioInfoAdmin(admin.ModelAdmin):
    list_display = ('techinfo',
                    'track_title',
                    'track_artist',
                    'track_duration',
                    'need_mic',
                    'confirm_no_music')


class LightingInfoAdmin(admin.ModelAdmin):
    list_display = ('techinfo', 'notes', 'costume')


class CueInfoAdmin(admin.ModelAdmin):
    list_display = ('techinfo', 'cue_sequence')


class BidEvalAdmin(admin.ModelAdmin):
    list_display = ('bid', 'evaluator', 'vote', 'notes')


class ClassProposalAdmin(admin.ModelAdmin):
    list_display = ('title', 'name', 'email', 'type', 'display')


class ConferenceVolunteerAdmin(admin.ModelAdmin):
    list_display = ('presenter',
                    'bid',
                    'how_volunteer',
                    'qualification',
                    'volunteering')
    list_filter = ['presenter', 'bid', 'how_volunteer']


class ProfilePreferencesAdmin(admin.ModelAdmin):
    list_display = ('profile',
                    'in_hotel',
                    'inform_about',
                    'show_hotel_infobox')
    list_filter = ['in_hotel', 'inform_about']


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'overbook_size')


class ShowAdmin(admin.ModelAdmin):
    list_filter = ['e_conference__conference_slug']


class GenericAdmin(ImportExportActionModelAdmin):
    list_display = ('e_title', 'type')
    list_filter = ['e_conference', 'type', 'visible']
    search_fields = ['e_title']


class EventAdmin(admin.ModelAdmin):
    list_display = ('eventitem_id', 'e_title', 'subclass')
    list_filter = ['e_conference__conference_slug']
    search_fields = ['e_title']

    def subclass(self, obj):
        event = Event.objects.get_subclass(event_id=obj.event_id)
        return str(event.__class__.__name__)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('view',
                    'code',
                    'summary',
                    'description')
    list_editable = ('summary', 'description')
    readonly_fields = ('view', 'code')
    list_filter = ['view', 'code']


class AvailableInterestAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'interest',
                    'visible',
                    'help_text')
    list_editable = ('interest',
                     'visible',
                     'help_text')


class VolunteerInterestAdmin(admin.ModelAdmin):
    list_display = ('interest',
                    'volunteer',
                    'rank',
                    'conference')
    list_filter = ['interest',
                   'rank',
                   'volunteer__b_conference__conference_slug']

    def conference(self, obj):
        return obj.volunteer.b_conference


class VolunteerWindowAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'day_w_year',
                    'start',
                    'end',
                    'conference')
    list_filter = ['day',
                   'day__conference__conference_slug']
    list_editable = ('start',
                     'end',)

    def conference(self, obj):
        return obj.day.conference

    def day_w_year(self, obj):
        return obj.day.day


class ConferenceDayAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'day',
                    'conference',
                    'open_to_public')
    list_filter = ['conference__conference_slug']
    list_editable = ('day',
                     'conference',
                     'open_to_public')


class EmailTemplateSenderAdmin(admin.ModelAdmin):
    list_display = ('template',
                    'from_email')
    list_editable = ('from_email', )
    list_display_links = None


class CastingAdmin(admin.ModelAdmin):
    list_display = ('casting',
                    'show_as_special',
                    'display_order',)
    list_editable = ('casting',
                     'show_as_special',
                     'display_order',)
    list_display_links = None


class FlexibleEvalAdmin(admin.ModelAdmin):
    list_display = ('bid',
                    'evaluator',
                    'category',
                    'ranking')
    list_filter = ['category', ]


class EvalCategoryAdmin(admin.ModelAdmin):
    list_display = ('category',
                    'visible',
                    'help_text')
    list_filter = ['visible', ]

admin.site.register(Conference, ConferenceAdmin)
admin.site.register(ConferenceDay, ConferenceDayAdmin)
admin.site.register(VolunteerWindow, VolunteerWindowAdmin)
admin.site.register(VolunteerInterest, VolunteerInterestAdmin)
admin.site.register(AvailableInterest, AvailableInterestAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Biddable, BidAdmin)
admin.site.register(Act, ActAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Vendor, BidAdmin)
admin.site.register(Volunteer, BidAdmin)
admin.site.register(Costume, BidAdmin)
admin.site.register(Show, ShowAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(ClassProposal, ClassProposalAdmin)
admin.site.register(ActBidEvaluation)
admin.site.register(BidEvaluation, BidEvalAdmin)
admin.site.register(TechInfo)
admin.site.register(AudioInfo, AudioInfoAdmin)
admin.site.register(LightingInfo, LightingInfoAdmin)
admin.site.register(CueInfo, CueInfoAdmin)
admin.site.register(StageInfo)
admin.site.register(PerformerFestivals)
admin.site.register(ProfilePreferences, ProfilePreferencesAdmin)
admin.site.register(Persona, PerformerAdmin)
admin.site.register(Performer, PerformerAdmin)
admin.site.register(Combo, PerformerAdmin)
admin.site.register(Troupe, TroupeAdmin)
admin.site.register(ConferenceVolunteer, ConferenceVolunteerAdmin)
admin.site.register(GenericEvent, GenericAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(UserMessage, MessageAdmin)
admin.site.register(ShowVote)
admin.site.register(FlexibleEvaluation, FlexibleEvalAdmin)
admin.site.register(EvaluationCategory, EvalCategoryAdmin)
admin.site.register(EmailTemplateSender, EmailTemplateSenderAdmin)
admin.site.register(ActCastingOption, CastingAdmin)
