# Generated by Django 3.2.18 on 2023-05-15 19:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0035_remove_worker_models'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Performer',
        ),
        migrations.DeleteModel(
            name='Persona',
        ),
        migrations.DeleteModel(
            name='Troupe',
        ),
        migrations.RemoveField(
            model_name='flexibleevaluation',
            name='evaluator',
        ),
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
