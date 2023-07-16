# Generated by Django 4.2.3 on 2023-07-07 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_feed', '0014_alert_country_source_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='identifier',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alert',
            name='scope',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alert',
            name='sent',
            field=models.DateTimeField(default=(1970, 1, 1, 0, 0, 0, 3, 1, 0)),
        ),
        migrations.AlterField(
            model_name='source',
            name='format',
            field=models.CharField(choices=[('meteoalarm', 'meteoalarm'), ('capfeedphp', 'capfeedphp'), ('capusphp', 'capusphp')]),
        ),
    ]