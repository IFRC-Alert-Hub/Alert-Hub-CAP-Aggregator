# Generated by Django 4.2.3 on 2023-07-26 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cap_feed', '0002_feed_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedlog',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
    ]
