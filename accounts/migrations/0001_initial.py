# Generated by Django 5.0.1 on 2024-01-25 15:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('original', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user_from', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rel_from_set', to=settings.AUTH_USER_MODEL)),
                ('user_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rel_to_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_locked', models.BooleanField(default=False)),
                ('email', models.CharField(max_length=300)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('bio', models.TextField()),
                ('photo', models.ImageField(blank=True, upload_to='users/%Y/%m/%d/')),
                ('bg_photo', models.ImageField(blank=True, upload_to='users/%Y/%m/%d')),
                ('disable_chat', models.BooleanField(default=False)),
                ('user_type', models.CharField(choices=[('Bloger', 'Bloger'), ('Software engineering', 'Software Engineering'), ('Graphic designer', 'Graphic Designer'), ('Football player', 'Football Player'), ('Musician', 'Musician'), ('SMM manager', 'Smm Manager'), ('Marketology', 'Marketology')], default='Bloger', max_length=100)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('following', models.ManyToManyField(blank=True, related_name='followers', through='accounts.Contact', to='accounts.profile')),
                ('saved_posts', models.ManyToManyField(blank=True, related_name='saved_by', to='original.post')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['-created'], name='accounts_co_created_07cffc_idx'),
        ),
    ]