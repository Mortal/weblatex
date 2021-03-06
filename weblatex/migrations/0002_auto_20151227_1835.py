# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-27 18:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weblatex', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookletentry',
            options={'ordering': ['booklet', 'page', 'position']},
        ),
        migrations.RenameField(
            model_name='bookletentry',
            old_name='order',
            new_name='page',
        ),
        migrations.AddField(
            model_name='bookletentry',
            name='position',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
