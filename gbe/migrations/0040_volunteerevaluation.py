# Generated by Django 3.2.18 on 2023-07-10 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0039_auto_20230519_2133'),
    ]

    operations = [
        migrations.CreateModel(
            name='VolunteerEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote', models.IntegerField(choices=[(1, 'Strong yes'), (2, 'Yes'), (3, 'Weak Yes'), (4, 'No Comment'), (5, 'Weak No'), (6, 'No'), (7, 'Strong No'), (-1, 'Abstain')])),
                ('notes', models.TextField(blank=True)),
                ('conference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gbe.conference')),
                ('evaluator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evals_from', to='gbe.profile')),
                ('volunteer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evals_for', to='gbe.profile')),
            ],
            options={
                'ordering': ['conference', 'volunteer', 'evaluator'],
                'unique_together': {('evaluator', 'volunteer', 'conference')},
            },
        ),
    ]
