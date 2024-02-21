# Generated by Django 4.2.9 on 2024-02-13 08:54

from django.db import migrations, models

def set_default_ride_id(apps, schema_editor):
    SalikDetails = apps.get_model('customer', 'SalikDetails')
    # Update existing rows with a default value for Ride_ID
    SalikDetails.objects.filter(Ride_ID__isnull=True).update(Ride_ID='default_value')

def set_default_value(apps, schema_editor):
    SalikDetails = apps.get_model('customer', 'SalikDetails')
    SalikDetails.objects.filter(UserId__isnull=True).update(UserId=0)

class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_salikdetails_ride_id_salikdetails_userid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salikdetails',
            name='Ride_ID',
            field=models.CharField(max_length=60, default='default_value', blank=True, null=True),
        ),
        migrations.RunPython(set_default_ride_id),
        migrations.AlterField(
            model_name='salikdetails',
            name='UserId',
            field=models.IntegerField(default=0),  # Set a temporary default value
        ),
        migrations.RunPython(set_default_value),  # Update existing rows with default value
    ]
