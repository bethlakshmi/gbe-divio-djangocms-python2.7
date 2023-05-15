# Generated by Django 3.2.18 on 2023-05-12 10:24

from django.db import migrations


def move_performer(performer, bio):
    # Move act proposals
    for act in performer.acts.all():
        act.bio = bio
        act.save()

    # Move social links
    for link in performer.links.all():
        link.bio = bio
        link.save()


def migrate_personas(apps, schema_editor):
    Bio = apps.get_model("gbe", "Bio")
    Persona = apps.get_model("gbe", "Persona")
    print('')
    print("migrating %d personas" % Persona.objects.all().count())
    for performer in Persona.objects.all():
        # move persona to bio
        bio = Bio(contact=performer.contact,
                  name=performer.name,
                  label=performer.label,
                  bio=performer.bio,
                  experience=performer.experience,
                  year_started=performer.year_started,
                  awards=performer.awards,
                  img=performer.img,
                  festivals=performer.festivals,
                  pronouns=performer.pronouns,
                  multiple_performers=False)
        bio.save()
        # Move class proposals
        for class_bid in performer.is_teaching.all():
            class_bid.teacher_bio = bio
            class_bid.save()

        # Move costume proposals
        for costume in performer.costume_set.all():
            costume.bio = bio
            costume.save()
        move_performer(performer, bio)


def migrate_troupes(apps, schema_editor):
    Bio = apps.get_model("gbe", "Bio")
    Troupe = apps.get_model("gbe", "Troupe")
    People = apps.get_model("scheduler", "People")
    print("migrating %d troupes" % Troupe.objects.all().count())
    for performer in Troupe.objects.all():
        # move persona to bio
        bio = Bio(contact=performer.contact,
                  name=performer.name,
                  label=performer.label,
                  bio=performer.bio,
                  experience=performer.experience,
                  year_started=performer.year_started,
                  awards=performer.awards,
                  img=performer.img,
                  festivals=performer.festivals,
                  pronouns=performer.pronouns,
                  multiple_performers=True)
        bio.save()
        move_performer(performer, bio)
        people = People(class_name=bio.__class__.__name__,
                        class_id=bio.pk)
        people.save()
        for member in performer.membership.all():
            people.users.add(member.performer_profile.user_object)


def migrate_profiles(apps, schema_editor):
    Profile = apps.get_model("gbe", "Profile")
    Account = apps.get_model("gbe", "Account")
    print("migrating %d profiles" % Profile.objects.all().count())
    for profile in Profile.objects.all():
        # move persona to bio
        account = Account(user_object=profile.user_object,
                          display_name=profile.display_name,
                          purchase_email=profile.purchase_email,
                          address1=profile.address1,
                          address2=profile.address2,
                          city=profile.city,
                          state=profile.state,
                          zip_code=profile.zip_code,
                          country=profile.country,
                          phone=profile.phone,
                          best_time=profile.best_time,
                          how_heard=profile.how_heard)
        account.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0033_new_bios'),
        ('scheduler', '0011_new_bios'),
    ]

    operations = [
        migrations.RunPython(migrate_profiles),
        migrations.RunPython(migrate_personas),
        migrations.RunPython(migrate_troupes)
    ]
