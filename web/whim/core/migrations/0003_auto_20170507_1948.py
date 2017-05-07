# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-07 19:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20170506_1019'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('last_modified_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=75)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='core.Category'),
            preserve_default=False,
        ),
    ]
