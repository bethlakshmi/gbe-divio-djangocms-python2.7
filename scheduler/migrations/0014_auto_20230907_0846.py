# Generated by Django 3.2.18 on 2023-09-07 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0013_remove_worker_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='people',
            name='commitment_class_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='people',
            name='commitment_class_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='people',
            unique_together={('class_name',
                              'class_id',
                              'commitment_class_name',
                              'commitment_class_id')},
        ),
    ]