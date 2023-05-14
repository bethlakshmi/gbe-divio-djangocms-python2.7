# Generated by Django 3.2.18 on 2023-05-14 13:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('gbe', '0032_articleconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('label', models.CharField(blank=True, max_length=100)),
                ('bio', models.TextField()),
                ('experience', models.PositiveIntegerField(blank=True, null=True)),
                ('year_started', models.PositiveIntegerField(null=True)),
                ('awards', models.TextField(blank=True)),
                ('festivals', models.TextField(blank=True)),
                ('pronouns', models.CharField(blank=True, max_length=128)),
                ('multiple_performers', models.BooleanField(default=False)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.profile')),
                ('img', filer.fields.image.FilerImageField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_bio', to=settings.FILER_IMAGE_MODEL)),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'label')},
            },
        ),
        migrations.AddField(
            model_name='act',
            name='bio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='acts', to='gbe.bio'),
        ),
        migrations.AddField(
            model_name='class',
            name='teacher_bio',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='is_teaching', to='gbe.bio'),
        ),
        migrations.AddField(
            model_name='costume',
            name='bio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='gbe.bio'),
        ),
        migrations.AddField(
            model_name='sociallink',
            name='bio',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='links', to='gbe.bio'),
        ),
    ]
