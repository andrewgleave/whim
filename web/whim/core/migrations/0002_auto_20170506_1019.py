# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-06 10:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EventManager',
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['-start_datetime']},
        ),
        migrations.AddField(
            model_name='event',
            name='status',
            field=models.PositiveIntegerField(choices=[(0, 'Pending'), (1, 'Published'), (2, 'Removed'), (3, 'Needs Review')], default=0),
        ),
    ]