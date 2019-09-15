# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from django.core.files import File as DjangoFile
import os
from django.conf import settings
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder


def create_filer_images(apps, schema_editor):
    Performer = apps.get_model('gbe', 'Performer')

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
    except ImportError:
        from django.contrib.auth.models import User  # NOQA
    superuser = User.objects.create_superuser('admin_img',
                                              'admin@importimage.com',
                                              'secret')
    folder, created = Folder.objects.get_or_create(name='Performers')
    for performer in Performer.objects.all():
        if performer.promo_image:
            full_name = os.path.join(settings.MEDIA_ROOT,
                                     performer.promo_image.name)
            file_name = performer.promo_image.name.split(
                'uploads/images/', 1)[-1]
            print "\nPerformer: " + str(performer.name)
            print "File: " + file_name
            file_obj = DjangoFile(open(full_name, 'rb'),
                                  name=file_name)
            img, created = Image.objects.get_or_create(
                owner=superuser,
                original_filename=file_name,
                file=file_obj,
                folder=folder,
                author="%s_%d" % (str(performer.name), performer.pk)
            )
            img.save()
            performer.img_id = img.pk
            performer.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gbe', '0010_performer_img'),
    ]

    operations = [
        migrations.RunPython(create_filer_images),
    ]
