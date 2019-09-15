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
                    'resource_email',
                    'resource_type')
    list_filter = ['event__eventitem__event__e_conference',
                   'resource__worker__role',
                   'resource__location']

    def resource_email(self, obj):
        resource = Resource.objects.filter(allocations=obj)[0]
        return resource.item.contact_email

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

    def event_type(self, obj):
        if str(obj.child().__class__.__name__) == 'GenericEvent':
            return obj.child().type
        else:
            return str(obj.child().__class__.__name__)

    def conference(self, obj):
        return obj.child().e_conference


class EventAdmin(ImportExportModelAdmin):
    list_display = ('id', 'eventitem', 'starttime', 'max_volunteer')
    list_filter = ['starttime',
                   'max_volunteer',
                   'eventitem__event__e_conference', ]


class EventContainerAdmin(ImportExportModelAdmin):
    list_display = ('parent_event', 'child_event', 'child_conf')
    list_filter = ['parent_event__eventitem__event__e_conference']

    def child_conf(self, obj):
        return obj.child_event.eventitem.get_conference()


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('_item', 'role')
    list_filter = ['role', '_item']


class ActResourceAdmin(admin.ModelAdmin):
    list_display = ('_item', 'role')
    list_filter = ['role', '_item__act__b_conference']


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order', 'allocation')


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


admin.site.register(EventItem, EventItemAdmin)
admin.site.register(LocationItem)
admin.site.register(WorkerItem)
admin.site.register(ResourceItem)
admin.site.register(Event, EventAdmin)
admin.site.register(Location)
admin.site.register(Worker, WorkerAdmin)
admin.site.register(Resource)
admin.site.register(ResourceAllocation, ResourceAllocationAdmin)
admin.site.register(ActItem)
admin.site.register(Ordering, OrderAdmin)
admin.site.register(ActResource, ActResourceAdmin)
admin.site.register(EventContainer, EventContainerAdmin)
admin.site.register(EventLabel, EventLabelAdmin)
