# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def add_default_sender(apps, schema_editor):
    EmailTemplateSender = apps.get_model("gbe", "EmailTemplateSender")
    EmailTemplate = apps.get_model("post_office", "EmailTemplate")
    for template in EmailTemplate.objects.all():
        sender = EmailTemplateSender(template=template,
                                     from_email=settings.DEFAULT_FROM_EMAIL)
        sender.save()

def reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0004_auto_20160607_0901'),
        ('gbe', '0003_auto_20170312_2031'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplateSender',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_email', models.EmailField(max_length=254)),
                ('template', models.OneToOneField(related_name='sender', to='post_office.EmailTemplate')),
            ],
            options={
                'ordering': ['template__name'],
            },
        ),
        migrations.RunPython(add_default_sender, reverse),
    ]
