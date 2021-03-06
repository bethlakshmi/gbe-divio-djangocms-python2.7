# Generated by Django 3.0.12 on 2021-02-18 07:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gbe', '0004_auto_20201224_1145'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserStylePreview',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('previewer', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to=settings.AUTH_USER_MODEL)),
                ('version', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='gbe.StyleVersion')),
            ],
        ),
    ]
