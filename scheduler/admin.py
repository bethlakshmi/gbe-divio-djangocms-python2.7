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
                   'resource__location']
    autocomplete_fields = ['event', 'resource']

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["event"].help_text = event_search_guide
        form.base_fields["resource"].help_text = resource_search_guide
        return form

    def resource_type(self, obj):
        resource = Resource.objects.filter(allocations=obj)[0]
        return resource.type

    def event_type(self, obj):
        return str(obj.event.event_style)


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'type',
                    'as_subtype')
    search_fields = ['id', 'location']


class PeopleAllocationAdmin(ImportExportActionModelAdmin):
    list_display = ('id',
                    'event',
                    'event_type',
                    'people_id',
                    'role',
                    'label',
                    'user_list')
    list_filter = ['event__event_style',
                   'event__eventlabel__text',
                   'role',
                   'people__class_name']
    search_fields = ['people__users__profile__display_name',
                     'people__users__username',
                     'people__users__email',
                     'event__title',
                     'people__commitment_class_id']
    autocomplete_fields = ['people', 'event']

    def user_list(self, obj):
        people = ""
        for person in obj.people.users.all():
            people = person.profile.display_name + ', ' + people
        return people

    def people_id(self, obj):
        return obj.people.pk

    def event_type(self, obj):
        return str(obj.event.event_style)

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["event"].help_text = event_search_guide
        return form


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
    search_fields = ['title', 'event_style', 'id']
    autocomplete_fields = ['parent', 'peer']

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["parent"].help_text = event_search_guide
        form.base_fields["peer"].help_text = event_search_guide
        return form


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order',
                    'performer',
                    'people_id',
                    'role',
                    'event',
                    'people')
    list_filter = ['people_allocated__event', ]
    search_fields = ['people_allocated__people__users__profile__display_name',
                     'people_allocated__people__users__username',
                     'people_allocated__people__users__email',
                     'people_allocated__event__title',
                     'people_allocated__people__commitment_class_id']
    autocomplete_fields = ['people_allocated']

    def event(self, obj):
        return obj.people_allocated.event

    def performer(self, obj):
        return "class: %s, id: %d" % (obj.people_allocated.people.class_name,
                                      obj.people_allocated.people.class_id)

    def people(self, obj):
        people = ""
        for person in obj.people_allocated.people.users.all():
            people = person.profile.display_name + ', ' + people
        return people

    def people_id(self, obj):
        return obj.people_allocated.people.pk


class PeopleAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'class_name',
                    'class_id',
                    'commitment_class_id',
                    'user_list')
    list_filter = ['class_name']
    search_fields = ['users__username',
                     'users__profile__display_name',
                     'class_id',
                     'commitment_class_id']
    filter_horizontal = ("users",)

    def user_list(self, obj):
        people = ""
        for person in obj.users.all():
            people = person.profile.display_name + ', ' + people
        return people


class EventLabelAdmin(admin.ModelAdmin):
    list_display = ('text', 'event')
    list_filter = ['text']
    autocomplete_fields = ['event']

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        form.base_fields["event"].help_text = event_search_guide
        return form


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


admin.site.register(Event, EventAdmin)
admin.site.register(EventLabel, EventLabelAdmin)
admin.site.register(Location)
admin.site.register(LocationItem)
admin.site.register(Ordering, OrderAdmin)
admin.site.register(ResourceItem)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceAllocation, ResourceAllocationAdmin)
admin.site.register(PeopleAllocation, PeopleAllocationAdmin)
admin.site.register(People, PeopleAdmin)
