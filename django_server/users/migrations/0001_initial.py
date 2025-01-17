# Generated by Django 5.0.6 on 2024-07-23 09:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.IntegerField()),
                ('language', models.CharField(choices=[('kk', 'Kazakh'), ('ru', 'Russian')], default='kz', max_length=2)),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('supervisor', 'Supervisor'), ('mentor', 'Mentor')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.IntegerField()),
                ('language', models.CharField(choices=[('kk', 'Kazakh'), ('ru', 'Russian')], default='kz', max_length=2)),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=100)),
                ('role', models.CharField(choices=[('shop', 'Shop'), ('security', 'Security'), ('support', 'Support'), ('office', 'Office')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('first_day', models.DateField(blank=True, null=True)),
                ('mentor', models.ForeignKey(blank=True, limit_choices_to={'role': 'mentor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mentees', to='users.manager')),
                ('supervisor', models.ForeignKey(blank=True, limit_choices_to={'role': 'supervisor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subordinates', to='users.manager')),
            ],
        ),
    ]
