# Generated by Django 3.2.18 on 2023-10-21 19:39

from django.db import migrations


def port_act_show_pref(apps, schema_editor):
    Act = apps.get_model("gbe", "Act")
    print("")
    for act in Act.objects.filter(b_conference__act_style="summer"):
        act.shows_preferences = []
        act.save()

    print("cleared prefs from %d acts" % Act.objects.filter(
        b_conference__act_style="summer").count())


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0042_auto_20230905_1112'),
    ]

    operations = [
        migrations.RunPython(port_act_show_pref),
    ]
