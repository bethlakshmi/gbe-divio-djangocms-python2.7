# Generated by Django 3.2.18 on 2023-05-14 21:05

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(blank=True, max_length=128)),
                ('purchase_email', models.CharField(blank=True, default='', max_length=64)),
                ('address1', models.CharField(blank=True, max_length=128)),
                ('address2', models.CharField(blank=True, max_length=128)),
                ('city', models.CharField(blank=True, max_length=128)),
                ('state', models.CharField(blank=True, choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('OTHER', 'Other/Non-US')], max_length=5)),
                ('zip_code', models.CharField(blank=True, max_length=10)),
                ('country', models.CharField(blank=True, max_length=128)),
                ('phone', models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='Phone numbers must be in a standard US format, such as ###-###-####.', regex='(\\d{3}[-\\.]?\\d{3}[-\\.]?\\d{4})')])),
                ('best_time', models.CharField(blank=True, choices=[('Any', 'Any'), ('Mornings', 'Mornings'), ('Afternoons', 'Afternoons'), ('Evenings', 'Evenings')], default='Any', max_length=50)),
                ('how_heard', models.TextField(blank=True)),
                ('user_object', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['display_name'],
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
