from django.contrib import admin
from ticketing.models import *


class PayPalSettingsAdmin(admin.ModelAdmin):
    list_display = ('business_email', )


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('ticket_item',
                    'purchaser',
                    'amount',
                    'order_date',
                    'import_date')
    list_filter = ['order_date',
                   'import_date']
    search_fields = ['ticket_item__title',
                     'purchaser__matched_to_user__username']


class PurchaserAdmin(admin.ModelAdmin):
    list_display = ('matched_to_user',
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
                   'bpt_event',
                   'live',
                   'has_coupon']
    search_fields = ['title']

    def conference(self, obj):
        return obj.bpt_event.conference

    def active(self, obj):
        return obj.active


class DetailInline(admin.TabularInline):
    model = EventDetail


class BPTEventsAdmin(admin.ModelAdmin):
    filter_horizontal = ("linked_events",)
    search_fields = ('title', )
    list_display = ('title',
                    'bpt_event_id',
                    'primary',
                    'act_submission_event',
                    'vendor_submission_event',
                    'include_conference',
                    'include_most')
    list_filter = ['conference',
                   'primary',
                   'act_submission_event',
                   'vendor_submission_event',
                   'badgeable',
                   ]
    inlines = [
        DetailInline,
    ]
    fieldsets = (
        ("Control Fields", {
            'fields': ('bpt_event_id', 'conference',),
            'description': '''Use the event id from BPT.  Conference controls
                where events are displayed - only active/upcoming conferences
                are synced.''',
        }),
        ('Event Links', {
            'fields': ('primary',
                       'act_submission_event',
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
                BPT but not shown.  Display Icon must come from
                http://simplelineicons.com/ -- NOTE:  Avoid the "."''',
        }),
    )


class TicketingExclusionInline(admin.TabularInline):
    model = TicketingExclusion
    filter_horizontal = ("tickets",)


class RoleExclusionInline(admin.TabularInline):
    model = RoleExclusion


class EligibilityConditionAdmin(admin.ModelAdmin):
    list_display = ('__str__',
                    'checklistitem')
    list_filter = ['checklistitem']
    inlines = [
        TicketingExclusionInline,
        RoleExclusionInline
    ]


class TicketEligibilityConditionAdmin(admin.ModelAdmin):
    filter_horizontal = ("tickets",)
    list_display = ('__str__',
                    'checklistitem')
    list_filter = ['checklistitem']
    inlines = [
        TicketingExclusionInline,
        RoleExclusionInline
    ]


admin.site.register(BrownPaperSettings)
admin.site.register(PayPalSettings, PayPalSettingsAdmin)
admin.site.register(BrownPaperEvents, BPTEventsAdmin)
admin.site.register(TicketItem, TicketItemAdmin)
admin.site.register(Purchaser, PurchaserAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TicketingEligibilityCondition,
                    TicketEligibilityConditionAdmin)
admin.site.register(RoleEligibilityCondition,
                    EligibilityConditionAdmin)
admin.site.register(CheckListItem)
