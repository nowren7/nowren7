# Generated by Django 4.2.9 on 2024-02-14 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0010_alter_salikdetails_ride_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salikdetails',
            name='UserId',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
