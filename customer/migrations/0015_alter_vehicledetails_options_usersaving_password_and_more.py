from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0014_userlogin'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vehicledetails',
            options={'verbose_name': 'Vehicle', 'verbose_name_plural': 'Vehicles'},
        ),
        # Comment out or remove the migration operation related to adding the "Status" field
        # migrations.AddField(
        #     model_name='vehicledetails',
        #     name='Status',
        #     field=models.CharField(choices=[('Not started', 'Not started'), ('Pending', 'Pending'), ('Under process', 'Under process'), ('Upload Done', 'Upload Done'), ('Contract Closed', 'Contract Closed')], default='Not started', max_length=20),
        # ),
    ]
