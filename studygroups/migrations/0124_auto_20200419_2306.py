# Generated by Django 2.2.10 on 2020-04-19 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0123_studygroup_did_not_happen'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='email_address',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='team',
            name='intro_text',
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name='team',
            name='location',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='team',
            name='website',
            field=models.CharField(blank=True, max_length=128),
        ),
    ]
