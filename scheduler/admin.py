from django.contrib import admin
from scheduler.models import *
import datetime
from gbe_forms_text import *
from import_export.admin import (
    ImportExportActionModelAdmin,
    ImportExportModelAdmin,
)
from import_export.resources import ModelResource


class ResourceAllocationAdmin(ImportExportActionModelAdmin):
    list_display = ('id',
                    'event',
                    'event_type',
                    'resource',
                    'resource_type')
    list_filter = ['event__event_style',
                   'event__eventlabel__text',
                   'resource__worker__role',
                   'resource__location']

    def resource_type(self, obj):
        resource = Resource.objects.filter(allocations=obj)[0]
        return resource.type

    def event_type(self, obj):
        return str(obj.event.event_style)


class EventAdmin(ImportExportModelAdmin):
    list_display = ('id',
                    'title',
                    'length',
                    'event_style',
                    'connected_class',
                    'connected_id',
                    'slug',
                    'starttime',
                    'max_volunteer',
                    'max_commitments',
                    'labels')
    list_filter = ['event_style',
                   'starttime',
                   'max_volunteer',
                   'max_commitments',
                   'approval_needed', ]
    search_fields = ['title', 'event_style']


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('_item', 'role')
    list_filter = ['role', '_item']


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'performer', 'role', 'class_id')

    def performer(self, obj):
        return str(obj.allocation.resource)


class EventLabelAdmin(admin.ModelAdmin):
    list_display = ('text', 'event')
    list_filter = ['text']


@admin.register(EventEvalQuestion)
class EventEvalQuestionAdmin(admin.ModelAdmin):
    list_display = ('order',
                    'visible',
                    'question',
                    'help_text',)
    list_editable = ('order',
                     'visible',
                     'question',
                     'help_text',)
    list_display_links = None
    ordering = ['order', ]


@admin.register(EventEvalGrade, EventEvalComment, EventEvalBoolean)
class EventEvalGradeAdmin(admin.ModelAdmin):
    list_display = ('event',
                    'profile',
                    'question',
                    'answer',)
    list_editable = ('question',
                     'answer',)
    list_display_links = ('event',)


admin.site.register(Event, EventAdmin)
admin.site.register(EventLabel, EventLabelAdmin)
admin.site.register(Location)
admin.site.register(LocationItem)
admin.site.register(Ordering, OrderAdmin)
admin.site.register(ResourceItem)
admin.site.register(Resource)
admin.site.register(ResourceAllocation, ResourceAllocationAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(WorkerItem)
