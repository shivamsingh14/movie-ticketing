# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-05 06:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='booking_status',
            field=models.CharField(default='Confirmed', max_length=2048),
        ),
    ]
