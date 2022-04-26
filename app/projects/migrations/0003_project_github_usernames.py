# Generated by Django 4.0.1 on 2022-02-02 22:09

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_project_stripe_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='github_usernames',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=255), blank=True, null=True, size=None),
        ),
    ]
