# Generated by Django 5.2.1 on 2025-05-16 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='badge',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
