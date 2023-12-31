# Generated by Django 4.2.3 on 2023-08-10 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_feed', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feed',
            name='enable_polling',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='feed',
            name='enable_rebroadcast',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='feed',
            name='status',
            field=models.CharField(choices=[('active', 'active'), ('unusable', 'unusable'), ('inactive', 'inactive'), ('testing', 'testing')], default='active'),
        ),
    ]
