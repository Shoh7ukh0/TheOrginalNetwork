# Generated by Django 5.0 on 2023-12-23 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('original', '0014_savedpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
    ]