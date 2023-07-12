# Generated by Django 4.2.3 on 2023-07-12 15:28

import cap_feed.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cap_feed', '0016_remove_alert_area_desc_remove_alert_certainty_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='addresses',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='alert',
            name='code',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alert',
            name='incidents',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='alert',
            name='note',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='alert',
            name='references',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='alert',
            name='restriction',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alert',
            name='source',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='audience',
            field=models.CharField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='category',
            field=models.CharField(choices=[('Geo', 'Geo'), ('Met', 'Met'), ('Safety', 'Safety'), ('Security', 'Security'), ('Rescue', 'Rescue'), ('Fire', 'Fire'), ('Health', 'Health'), ('Env', 'Env'), ('Transport', 'Transport'), ('Infra', 'Infra'), ('CBRNE', 'CBRNE'), ('Other', 'Other')]),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='contact',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='effective',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='event_code',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='expires',
            field=models.DateTimeField(blank=True, default=cap_feed.models.AlertInfo.default_expire),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='headline',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='instruction',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='language',
            field=models.CharField(blank=True, default='en-US', max_length=255),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='onset',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='parameter',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='response_type',
            field=models.CharField(blank=True, choices=[('Shelter', 'Shelter'), ('Evacuate', 'Evacuate'), ('Prepare', 'Prepare'), ('Execute', 'Execute'), ('Avoid', 'Avoid'), ('Monitor', 'Monitor'), ('Assess', 'Assess'), ('AllClear', 'AllClear'), ('None', 'None')], default=''),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='sender_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='alertinfo',
            name='web',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='atom',
            field=models.CharField(default='http://www.w3.org/2005/Atom', editable=False),
        ),
        migrations.AlterField(
            model_name='source',
            name='cap',
            field=models.CharField(default='urn:oasis:names:tc:emergency:cap:1.2', editable=False),
        ),
        migrations.AlterField(
            model_name='source',
            name='format',
            field=models.CharField(choices=[('meteoalarm', 'meteoalarm'), ('aws', 'aws'), ('nws_us', 'nws_us')]),
        ),
        migrations.CreateModel(
            name='InfoArea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_desc', models.TextField()),
                ('altitude', models.CharField(blank=True, default='')),
                ('ceiling', models.CharField(blank=True, default='')),
                ('alert_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cap_feed.alertinfo')),
            ],
        ),
        migrations.CreateModel(
            name='AreaPolygon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('info_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cap_feed.infoarea')),
            ],
        ),
        migrations.CreateModel(
            name='AreaGeocode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value_name', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('info_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cap_feed.infoarea')),
            ],
        ),
        migrations.CreateModel(
            name='AreaCircle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('info_area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cap_feed.infoarea')),
            ],
        ),
    ]
