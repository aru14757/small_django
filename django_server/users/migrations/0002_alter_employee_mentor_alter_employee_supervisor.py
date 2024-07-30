# Generated by Django 5.0.6 on 2024-07-26 08:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='mentor',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'mentor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mentored_employees', to='users.manager'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='supervisor',
            field=models.ForeignKey(blank=True, limit_choices_to={'role': 'supervisor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='supervised_employees', to='users.manager'),
        ),
    ]