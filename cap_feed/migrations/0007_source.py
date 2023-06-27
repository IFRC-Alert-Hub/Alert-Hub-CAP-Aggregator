# Generated by Django 4.2.2 on 2023-06-26 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_feed', '0006_alert_effective'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('url', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('polling_interval', models.IntegerField(choices=[(30, '00:30'), (45, '00:45'), (60, '01:00'), (75, '01:15'), (90, '01:30'), (105, '01:45'), (120, '02:00')])),
                ('verification_keys', models.CharField(blank=True, max_length=255, null=True)),
                ('iso3', models.CharField(max_length=255)),
                ('format', models.CharField(max_length=255)),
                ('atom', models.CharField(max_length=255)),
                ('cap', models.CharField(max_length=255)),
            ],
        ),
    ]
