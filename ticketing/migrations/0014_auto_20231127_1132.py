# Generated by Django 3.2.18 on 2023-11-27 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketing', '0013_eventbritesettings_organizer_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaser',
            name='address',
        ),
        migrations.RemoveField(
            model_name='purchaser',
            name='city',
        ),
        migrations.RemoveField(
            model_name='purchaser',
            name='country',
        ),
        migrations.RemoveField(
            model_name='purchaser',
            name='state',
        ),
        migrations.RemoveField(
            model_name='purchaser',
            name='zip',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='order_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='payment_source',
            field=models.CharField(default='Manual', max_length=30),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='reference',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='shipping_method',
            field=models.CharField(default='electronic', max_length=50),
        ),
    ]
