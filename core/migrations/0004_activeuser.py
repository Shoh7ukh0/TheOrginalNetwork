# Generated by Django 5.0 on 2023-12-28 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_messagemodel_image'),
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