from django.contrib import admin
from gbe.models import *
from import_export.admin import ImportExportActionModelAdmin
from django.urls import reverse
from django.utils.html import format_html


class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('conference_name',
                    'conference_slug',
                    'status',
                    'accepting_bids')
    list_filter = ['status', 'act_style']


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
    list_display = ('b_title',
                    'profiles',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    list_filter = ['submitted', 'accepted', 'b_conference__conference_slug']


class ClassAdmin(BidAdmin):
    list_display = ('b_title',
                    'teacher',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    search_fields = ['e_title', 'teacher__name']


class ActAdmin(BidAdmin):
    list_display = ('performer',
                    'b_title',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    search_fields = ['b_title', 'performer__name']


class PerformerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'label')
    search_fields = ['name', 'contact__display_name']


class TroupeAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')
    filter_horizontal = ("membership",)


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_object', 'phone', 'purchase_email')
    search_fields = ['display_name',
                     'user_object__email']


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
    search_fields = ['profile__display_name',
                     'profile__user_object__email']


class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'overbook_size')
    list_filter = ['conferences']


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
                    'display_header',
                    'display_order',)
    list_editable = ('casting',
                     'show_as_special',
                     'display_header',
                     'display_order',)
    list_display_links = None


class EvalCategoryAdmin(admin.ModelAdmin):
    list_display = ('category',
                    'visible',
                    'help_text')
    list_filter = ['visible', ]


class StyleSelectorAdmin(ImportExportActionModelAdmin):
    list_display = (
        'pk',
        'selector',
        'pseudo_class',
        'used_for',
        'description')
    list_editable = (
        'selector',
        'pseudo_class',
        'used_for')


class StylePropertyAdmin(ImportExportActionModelAdmin):
    list_display = (
        'pk',
        'selector',
        'style_property',
        'value_type')
    list_editable = (
        'style_property',
        'value_type')
    list_filter = [
        'selector',
        'style_property']


class StyleValueAdmin(ImportExportActionModelAdmin):
    list_display = (
        'pk',
        'style_version',
        'style_property',
        'value',
        'image')
    list_editable = ('value', )
    list_filter = [
        'style_version__name',
        'style_version__number',
        'style_property__selector__selector',
        'style_property__selector__pseudo_class',
        'style_property__style_property']


class StyleVersionAdmin(ImportExportActionModelAdmin):
    list_display = (
        'name',
        'number',
        'currently_live',
        'currently_test')


class UserStylePreviewAdmin(admin.ModelAdmin):
    list_display = (
        'version',
        'previewer')


class VendorAdmin(BidAdmin):
    list_display = (
        'pk',
        'link_to_biz',
        'owners',
        'submitted',
        'accepted',
        'created_at',
        'updated_at')

    def link_to_biz(self, obj):
        link = reverse("admin:gbe_business_change",
                       args=[obj.business.id])
        return format_html('<a href="{}">{}</a>', link, obj.business.name)
    link_to_biz.short_description = 'Business'

    def owners(self, obj):
        return obj.business.show_owners(False)


class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'show_owners')

    def show_owners(self, obj):
        return obj.show_owners(False)


class FlexAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'bid',
        'category',
        'evaluator',
        'ranking')


admin.site.register(ActCastingOption, CastingAdmin)
admin.site.register(Act, ActAdmin)
admin.site.register(Biddable, BidAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(ClassProposal, ClassProposalAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(ConferenceDay, ConferenceDayAdmin)
admin.site.register(ConferenceVolunteer, ConferenceVolunteerAdmin)
admin.site.register(Costume, BidAdmin)
admin.site.register(EvaluationCategory, EvalCategoryAdmin)
admin.site.register(EmailTemplateSender, EmailTemplateSenderAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(FlexibleEvaluation, FlexAdmin)
admin.site.register(GenericEvent, GenericAdmin)
admin.site.register(PerformerFestivals)
admin.site.register(Performer, PerformerAdmin)
admin.site.register(Persona, PerformerAdmin)
admin.site.register(ProfilePreferences, ProfilePreferencesAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Show, ShowAdmin)
admin.site.register(StaffArea, StaffAreaAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(TechInfo)
admin.site.register(Business, BusinessAdmin)
admin.site.register(Troupe, TroupeAdmin)
admin.site.register(UserMessage, MessageAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Volunteer, BidAdmin)
admin.site.register(StyleValue, StyleValueAdmin)
admin.site.register(StyleProperty, StylePropertyAdmin)
admin.site.register(StyleSelector, StyleSelectorAdmin)
admin.site.register(StyleVersion, StyleVersionAdmin)
admin.site.register(UserStylePreview, UserStylePreviewAdmin)
