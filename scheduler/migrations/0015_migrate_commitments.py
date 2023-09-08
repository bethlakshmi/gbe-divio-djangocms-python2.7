# Generated by Django 3.2.18 on 2023-09-07 13:08

from django.db import migrations


def migrate_commitment(apps, schema_editor):
    Ordering = apps.get_model("scheduler", "Ordering")
    People = apps.get_model("scheduler", "People")

    created_count = 0
    print()
    print("existing unallocated people: %d" % People.objects.filter(
        peopleallocation__isnull=True).count())
    for commit in Ordering.objects.all():
        people, created = People.objects.get_or_create(
            class_name=commit.people_allocated.people.class_name,
            class_id=commit.people_allocated.people.class_id,
            commitment_class_name=commit.class_name,
            commitment_class_id=commit.class_id)
        for user in commit.people_allocated.people.users.all():
            people.users.add(user)
        commit.people_allocated.people = people
        commit.people_allocated.save()
        if created:
            created_count = created_count + 1

    deleted_count = People.objects.filter(
        peopleallocation__isnull=True).count()
    for people in People.objects.filter(peopleallocation__isnull=True):
        people.delete()
    print("created %d new people" % created_count)
    print("deleted %d new people" % deleted_count)

def migrate_commitment_reverse(apps, schema_editor):
    Ordering = apps.get_model("scheduler", "Ordering")
    People = apps.get_model("scheduler", "People")
    print()

    created_count = 0
    for commit in Ordering.objects.all():
        people, created = People.objects.get_or_create(
            class_name=commit.people_allocated.people.class_name,
            class_id=commit.people_allocated.people.class_id,
            commitment_class_name="",
            commitment_class_id=None)
        commit.class_id = commit.people_allocated.people.commitment_class_id
        commit.class_name = commit.people_allocated.people.commitment_class_name
        commit.save()
        for user in commit.people_allocated.people.users.all():
            people.users.add(user)
        commit.people_allocated.people = people
        commit.people_allocated.save()
        if created:
            created_count = created_count + 1

    deleted_count = People.objects.filter(
        peopleallocation__isnull=True).count()
    for people in People.objects.filter(peopleallocation__isnull=True):
        people.delete()
    print("created %d new people" % created_count)
    print("deleted %d new people" % deleted_count)


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0014_auto_20230907_0846'),
    ]

    operations = [
        migrations.RunPython(migrate_commitment,
                             reverse_code=migrate_commitment_reverse),
    ]
