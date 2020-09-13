# Generated by Django 3.0.8 on 2020-09-12 14:46

from django.db import migrations, models


def default_to_category(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Category = apps.get_model("gbe", "ActCastingOption")
    for category in Category.objects.all():
        category.display_header = category.casting
        if category.casting == "Regular Act":
            category.display_header = "Check out our fabulous Performers!"
        category.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='actcastingoption',
            name='display_header',
            field=models.CharField(default='', help_text='Displayed as header of event page', max_length=150),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='actcastingoption',
            name='casting',
            field=models.CharField(help_text='Displayed on act review page when making casting.', max_length=50, unique=True),
        ),
        migrations.RunPython(default_to_category)
    ]
