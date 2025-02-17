# Generated by Django 5.1.6 on 2025-02-14 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiapp', '0003_user_location_user_skill_profession'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='service',
        ),
        migrations.RemoveField(
            model_name='service',
            name='category',
        ),
        migrations.AddField(
            model_name='booking',
            name='services',
            field=models.ManyToManyField(to='apiapp.service'),
        ),
    ]
