# Generated by Django 4.2.3 on 2023-07-08 20:12

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cap_feed', '0015_alter_alert_identifier_alter_alert_scope_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alert',
            name='area_desc',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='certainty',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='description',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='effective',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='event',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='expires',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='geocode_name',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='geocode_value',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='senderName',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='severity',
        ),
        migrations.RemoveField(
            model_name='alert',
            name='urgency',
        ),
        migrations.AddField(
            model_name='alert',
            name='addresses',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='code',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='incidents',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='note',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='references',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='restriction',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='alert',
            name='source_feed',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='cap_feed.source'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='alert',
            name='identifier',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='alert',
            name='msg_type',
            field=models.CharField(choices=[('Alert', 'Alert'), ('Update', 'Update'), ('Cancel', 'Cancel'), ('Ack', 'Ack'), ('Error', 'Error')]),
        ),
        migrations.AlterField(
            model_name='alert',
            name='scope',
            field=models.CharField(choices=[('Public', 'Public'), ('Restricted', 'Restricted'), ('Private', 'Private')]),
        ),
        migrations.AlterField(
            model_name='alert',
            name='sent',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='alert',
            name='source',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='alert',
            name='status',
            field=models.CharField(choices=[('Actual', 'Actual'), ('Exercise', 'Exercise'), ('System', 'System'), ('Test', 'Test'), ('Draft', 'Draft')]),
        ),
        migrations.CreateModel(
            name='AlertInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(default='en-US', max_length=255)),
                ('category', models.CharField(choices=[('Geo', 'Geo'), ('capfeedphp', 'Met'), ('Safety', 'Safety'), ('Security', 'Security'), ('Rescue', 'Rescue'), ('Fire', 'Fire'), ('Health', 'Health'), ('Env', 'Env'), ('Transport', 'Transport'), ('Infra', 'Infra'), ('CBRNE', 'CBRNE'), ('Other', 'Other')])),
                ('event', models.CharField(max_length=255)),
                ('response_type', models.CharField(choices=[('Shelter', 'Shelter'), ('Evacuate', 'Evacuate'), ('Prepare', 'Prepare'), ('Avoid', 'Avoid'), ('Monitor', 'Monitor'), ('Assess', 'Assess'), ('AllClear', 'AllClear'), ('None', 'None')], null=True)),
                ('urgency', models.CharField(choices=[('Immediate', 'Immediate'), ('Expected', 'Expected'), ('Future', 'Future'), ('Past', 'Past'), ('Unknown', 'Unknown')])),
                ('severity', models.CharField(choices=[('Extreme', 'Extreme'), ('Severe', 'Severe'), ('Moderate', 'Moderate'), ('Minor', 'Minor'), ('Unknown', 'Unknown')])),
                ('certainty', models.CharField(choices=[('Observed', 'Observed'), ('Likely', 'Likely'), ('Possible', 'Possible'), ('Unlikely', 'Unlikely'), ('Unknown', 'Unknown')])),
                ('audience', models.CharField(null=True)),
                ('event_code', models.CharField(max_length=255, null=True)),
                ('effective', models.DateTimeField(default=django.utils.timezone.now)),
                ('onset', models.DateTimeField(null=True)),
                ('expires', models.DateTimeField(default=datetime.datetime(2023, 7, 9, 20, 12, 13, 728041, tzinfo=datetime.timezone.utc))),
                ('sender_name', models.CharField(max_length=255, null=True)),
                ('headline', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(null=True)),
                ('instruction', models.TextField(null=True)),
                ('web', models.URLField(null=True)),
                ('contact', models.CharField(max_length=255, null=True)),
                ('parameter', models.CharField(max_length=255, null=True)),
                ('alert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cap_feed.alert')),
            ],
        ),
    ]