# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-22 19:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weblatex', '0005_attribution_blank'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookletentry',
            name='attribution',
            field=models.BooleanField(default=True),
        ),
    ]