# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2019-06-13 20:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0118_teammembership_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='email_domain',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
