# Generated by Django 4.1 on 2023-03-22 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chattingapp', '0003_otp_checking'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='About',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='registered_userid',
            field=models.CharField(default='No', max_length=50),
        ),
    ]
