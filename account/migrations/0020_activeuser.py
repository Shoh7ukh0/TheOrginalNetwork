# Generated by Django 5.0 on 2023-12-30 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_remove_profile_is_online'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActiveUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=125)),
                ('is_admin', models.BooleanField(default=False)),
            ],
        ),
    ]