from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0016_usersaving_password'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='vehicledetails',
        #     name='Status',
        #     field=models.CharField(choices=[('Not started', 'Not started'), ('Pending', 'Pending'), ('Under process', 'Under process'), ('Upload Done', 'Upload Done'), ('Contract Closed', 'Contract Closed')], default='Not started', max_length=20),
        # ),
    ]
