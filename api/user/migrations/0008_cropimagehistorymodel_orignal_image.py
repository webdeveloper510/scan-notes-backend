# Generated by Django 4.2.23 on 2025-07-18 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_user', '0007_cropimagehistorymodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='cropimagehistorymodel',
            name='orignal_image',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
