# Generated by Django 5.0 on 2023-12-29 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_remove_profile_is_online_alter_profile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_online',
            field=models.BooleanField(default=False),
        ),
    ]