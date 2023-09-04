from django.contrib import admin
from gbe.models import *
from import_export.admin import ImportExportActionModelAdmin
from django.urls import reverse
from django.utils.html import format_html
from published.admin import (
    PublishedAdmin,
    add_to_list_display,
    add_to_readonly_fields,
)


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
                    'teacher_bio',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    search_fields = ['b_title', 'teacher_bio__name']


class ActAdmin(BidAdmin):
    list_display = ('bio',
                    'b_title',
                    'submitted',
                    'accepted',
                    'created_at',
                    'updated_at')
    search_fields = ['b_title', 'bio__name']


class PerformerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'contact', 'label')
    search_fields = ['name', 'contact__display_name']
    list_filter = ['multiple_performers']


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user_object', 'phone', 'purchase_email')
    search_fields = ['display_name',
                     'user_object__email']


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


class MessageAdmin(admin.ModelAdmin):
    search_fields = ('view',
                     'code',
                     'summary',
                     'description')
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
    search_fields = ['selector']


class StylePropertyAdmin(ImportExportActionModelAdmin):
    list_display = (
        'pk',
        'selector',
        'style_property',
        'value_type',
        'value_template',
        'element',
        'label')
    list_editable = (
        'style_property',
        'value_type',
        'value_template',
        'element',
        'label')
    list_filter = [
        'element',
        'label',
        'style_property']
    search_fields = ['selector__selector',
                     'selector__used_for',
                     'selector__description',
                     'style_property']


class SocialLinkAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'bio',
        'order',
        'social_network',
        'link',
        'username')
    list_filter = [
        'social_network',
        ]
    search_fields = ['bio__name',
                     'bio__contact__display_name',
                     ]


class StyleValueAdmin(ImportExportActionModelAdmin):
    list_display = (
        'pk',
        'style_version',
        'style_property',
        'value',
        'parseable_values',
        'image')
    list_editable = ('value', 'parseable_values')
    list_filter = [
        'style_version__name',
        'style_version__number',
        'style_property__selector__selector',
        'style_property__selector__pseudo_class',
        'style_property__style_property']
    search_fields = ['style_property__style_property',
                     'style_property__selector__selector']


class StyleVersionAdmin(ImportExportActionModelAdmin):
    list_display = (
        'name',
        'number',
        'currently_live',
        'currently_test')


class StyleGroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'order',
        'name',
        'test_notes')
    list_editable = (
        'order',
        'name',
        'test_notes')
    search_fields = ['name', 'test_urls']
    filter_horizontal = ("test_urls", )


class StyleElementAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'order',
        'name',
        'group',
        'description',
        'sample_html')
    list_editable = (
        'order',
        'name',
        'group',
        'description',
        'sample_html')
    list_filter = ['group', ]
    search_fields = ['group__name', 'name', 'description', 'sample_html']


class StyleLabelAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'order',
        'name',
        'group',
        'help_text')
    list_editable = (
        'order',
        'name',
        'group',
        'help_text')
    list_filter = ['group']
    search_fields = ['name', 'group__name', 'help_text']


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


class VolunteerEvalAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'volunteer',
        'vote',
        'evaluator',
        'conference')
    list_filter = ['conference']
    search_fields = ['volunteer__display_name',
                     'volunteer__user_object__email',
                     'volunteer__user_object__first',
                     'volunteer__user_object__last']


class EmailFrequencyAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'email_type',
        'weekday')


class ArticleAdmin(PublishedAdmin):
    readonly_fields = [] + add_to_readonly_fields()
    list_display = ['pk', 'title', ] + add_to_list_display()


admin.site.register(ActCastingOption, CastingAdmin)
admin.site.register(Act, ActAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Biddable, BidAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Conference, ConferenceAdmin)
admin.site.register(ConferenceDay, ConferenceDayAdmin)
admin.site.register(Costume, BidAdmin)
admin.site.register(EmailFrequency, EmailFrequencyAdmin)
admin.site.register(EvaluationCategory, EvalCategoryAdmin)
admin.site.register(EmailTemplateSender, EmailTemplateSenderAdmin)
admin.site.register(FlexibleEvaluation, FlexAdmin)
admin.site.register(Bio, PerformerAdmin)
admin.site.register(ProfilePreferences, ProfilePreferencesAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(StaffArea, StaffAreaAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(TechInfo)
admin.site.register(Business, BusinessAdmin)
admin.site.register(SocialLink, SocialLinkAdmin)
admin.site.register(UserMessage, MessageAdmin)
admin.site.register(Vendor, VendorAdmin)
admin.site.register(Volunteer, BidAdmin)
admin.site.register(VolunteerEvaluation, VolunteerEvalAdmin)
admin.site.register(StyleValue, StyleValueAdmin)
admin.site.register(StyleProperty, StylePropertyAdmin)
admin.site.register(StyleSelector, StyleSelectorAdmin)
admin.site.register(StyleVersion, StyleVersionAdmin)
admin.site.register(StyleGroup, StyleGroupAdmin)
admin.site.register(StyleElement, StyleElementAdmin)
admin.site.register(StyleLabel, StyleLabelAdmin)
admin.site.register(UserStylePreview, UserStylePreviewAdmin)
admin.site.register(TestURL)
