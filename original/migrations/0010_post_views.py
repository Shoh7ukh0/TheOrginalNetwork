# Generated by Django 4.2.7 on 2023-11-13 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('original', '0009_alter_comment_options_alter_post_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]