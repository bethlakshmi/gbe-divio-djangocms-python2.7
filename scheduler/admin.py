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
    list_filter = ['event__eventitem__event__e_conference',
                   'resource__worker__role',
                   'resource__location']

    def resource_type(self, obj):
        resource = Resource.objects.filter(allocations=obj)[0]
        return resource.type

    def event_type(self, obj):
        if str(obj.event.eventitem.child().__class__.__name__
               ) == 'GenericEvent':
            return obj.event.eventitem.child().type
        else:
            return str(obj.event.eventitem.child().__class__.__name__)


class EventItemAdmin(admin.ModelAdmin):
    list_display = (
        'eventitem_id', str, 'visible', 'event_type', 'conference')
    list_filter = ['visible', 'event__e_conference']
    search_fields = ['event__e_title']

    def event_type(self, obj):
        if str(obj.child().__class__.__name__) == 'GenericEvent':
            return obj.child().type
        else:
            return str(obj.child().__class__.__name__)

    def conference(self, obj):
        return obj.get_conference()


class EventAdmin(ImportExportModelAdmin):
    list_display = ('id',
                    'eventitem',
                    'title',
                    'duration',
                    'length',
                    'event_type',
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
                   'eventitem__event__e_conference',
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
admin.site.register(EventItem, EventItemAdmin)
admin.site.register(EventLabel, EventLabelAdmin)
admin.site.register(Location)
admin.site.register(LocationItem)
admin.site.register(Ordering, OrderAdmin)
admin.site.register(ResourceItem)
admin.site.register(Resource)
admin.site.register(ResourceAllocation, ResourceAllocationAdmin)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(WorkerItem)
