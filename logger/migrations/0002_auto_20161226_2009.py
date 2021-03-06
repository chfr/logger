# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-26 19:09
from __future__ import unicode_literals

import autoslug.fields
from django.db import migrations
import logger.models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datum',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False, populate_from='name', slugify=logger.models.underscore_slugify),
        ),
    ]
