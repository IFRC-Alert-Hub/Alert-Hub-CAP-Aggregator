# Generated by Django 4.2.2 on 2023-06-21 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_feed', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='polygon',
            field=models.TextField(blank=True, default='', max_length=16383),
        ),
        migrations.AlterField(
            model_name='alert',
            name='event',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alert',
            name='geocode_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alert',
            name='geocode_value',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
