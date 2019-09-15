# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from django.core.files import File as DjangoFile
import os
from django.conf import settings
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder


def create_filer_images(apps, schema_editor):
    Vendor = apps.get_model('gbe', 'Vendor')

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
    except ImportError:
        from django.contrib.auth.models import User  # NOQA
    superuser = User.objects.create_superuser('admin_img_vendor',
                                              'admin@importimage.com',
                                              'secret')
    folder, created = Folder.objects.get_or_create(name='Performers')
    for vendor in Vendor.objects.all():
        if vendor.logo:
            full_name = os.path.join(settings.MEDIA_ROOT,
                                     vendor.logo.name)
            file_name = vendor.logo.name.split(
                'uploads/images/', 1)[-1]
            print "\nVendor: " + str(vendor.b_title)
            print "File: " + file_name
            file_obj = DjangoFile(open(full_name, 'rb'),
                                  name=file_name)
            img, created = Image.objects.get_or_create(
                owner=superuser,
                original_filename=file_name,
                file=file_obj,
                folder=folder,
                author="%s_%d" % (str(vendor.b_title), vendor.pk)
            )
            img.save()
            vendor.img_id = img.pk
            vendor.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0015_auto_20170917_1910'),
    ]

    operations = [
        migrations.RunPython(create_filer_images),
    ]
