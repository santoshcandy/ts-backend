# Generated by Django 5.1.6 on 2025-02-14 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiapp', '0002_servicecategory_service_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='skill_profession',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
