from django.contrib import admin
from ticketing.models import *


class BrownPaperSettingsAdmin(admin.ModelAdmin):
    list_display = ('developer_token', 'client_username', 'last_poll_time')


class PayPalSettingsAdmin(admin.ModelAdmin):
    list_display = ('business_email', )


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('ticket_item',
                    'purchaser',
                    'amount',
                    'order_date',
                    'import_date')
    list_filter = ['ticket_item__ticketing_event__conference',
                   'order_date',
                   'import_date',
                   'ticket_item__ticketing_event__act_submission_event',
                   'ticket_item__ticketing_event__vendor_submission_event']
    search_fields = ['ticket_item__title',
                     'purchaser__matched_to_user__username',
                     'purchaser__email']


class PurchaserAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'matched_to_user',
                    'first_name',
                    'last_name',
                    'email',
                    'phone')
    list_filter = ['state',
                   'country']
    search_fields = ['matched_to_user__username',
                     'first_name',
                     'last_name',
                     'email']


class TicketItemAdmin(admin.ModelAdmin):
    list_display = ('title',
                    'ticket_id',
                    'active',
                    'cost',
                    'datestamp',
                    'modified_by',
                    'conference')
    list_filter = ['datestamp',
                   'modified_by',
                   'ticketing_event',
                   'live',
                   'has_coupon']
    search_fields = ['title']

    def conference(self, obj):
        return obj.ticketing_event.conference

    def active(self, obj):
        return obj.active


class DetailInline(admin.TabularInline):
    model = EventDetail


class TicketingEventsAdmin(admin.ModelAdmin):
    filter_horizontal = ("linked_events",)
    search_fields = ('title', 'event_id')
    list_display = ('title',
                    'event_id',
                    'act_submission_event',
                    'vendor_submission_event',
                    'include_conference',
                    'include_most')
    list_filter = ['conference',
                   'source',
                   'act_submission_event',
                   'vendor_submission_event',
                   'badgeable',
                   ]
    inlines = [
        DetailInline,
    ]
    fieldsets = (
        ("Control Fields", {
            'fields': ('event_id', 'conference',),
            'description': '''Use the event id from BPT.  Conference controls
                where events are displayed - only active/upcoming conferences
                are synced.''',
        }),
        ('Event Links', {
            'fields': ('act_submission_event',
                       'vendor_submission_event',
                       'include_conference',
                       'include_most',
                       "linked_events",),
            'description': '''Rules for what this ticket gives.  Controls
                when it's advertised and special actions like act/vendor submit
                ''',
        }),
        ("Registration", {
            'fields': ('badgeable', 'ticket_style'),
            'description': '''Older rules for registration.''',
            'classes': ('collapse',),
        }),
        ("Display Text", {
            'fields': ('display_icon', 'title', 'description'),
            'description': '''What is shown on the 'I Want to Buy Tickets'
                page.  Description is not shown there, it's pulled from
                ticket source but not shown.  Display Icon must come from
                https://simplelineicons.github.io/ or
                https://icons.getbootstrap.com/ -- NOTE:  Use only the
                classes, the i tag is already in the code.''',
        }),
    )


class TicketingExclusionInline(admin.TabularInline):
    model = TicketingExclusion
    filter_horizontal = ("tickets",)


class RoleExclusionInline(admin.TabularInline):
    model = RoleExclusion


class EligibilityConditionAdmin(admin.ModelAdmin):
    list_display = ('checklistitem', '__str__')
    list_filter = ['checklistitem']
    inlines = [
        TicketingExclusionInline,
        RoleExclusionInline
    ]


class TicketEligibilityConditionAdmin(admin.ModelAdmin):
    filter_horizontal = ("tickets",)
    list_display = ('checklistitem', '__str__')
    list_filter = ['checklistitem']
    inlines = [
        TicketingExclusionInline,
        RoleExclusionInline
    ]


class SyncStatusAdmin(admin.ModelAdmin):
    list_display = ('pk',
                    'is_success',
                    'import_type',
                    'import_number',
                    'error_msg',
                    'created_at',
                    'updated_at')


admin.site.register(BrownPaperSettings, BrownPaperSettingsAdmin)
admin.site.register(EventbriteSettings)
admin.site.register(PayPalSettings, PayPalSettingsAdmin)
admin.site.register(TicketingEvents, TicketingEventsAdmin)
admin.site.register(TicketItem, TicketItemAdmin)
admin.site.register(Purchaser, PurchaserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TicketingEligibilityCondition,
                    TicketEligibilityConditionAdmin)
admin.site.register(RoleEligibilityCondition,
                    EligibilityConditionAdmin)
admin.site.register(CheckListItem)
admin.site.register(SyncStatus, SyncStatusAdmin)
