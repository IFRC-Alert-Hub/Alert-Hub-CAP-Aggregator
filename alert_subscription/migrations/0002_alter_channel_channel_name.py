# Generated by Django 4.2.2 on 2023-06-30 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alert_subscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channel',
            name='channel_name',
            field=models.CharField(default='', max_length=255, primary_key=True, serialize=False),
        ),
    ]
