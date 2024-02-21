from django.db import migrations, models

def create_user_login(apps, schema_editor):
    # Your migration operations here, for example:
    Customer = apps.get_model('customer', 'Customer')
    # Add necessary fields or modify existing ones
    # For example:
    Customer.objects.create(username='example', password='password123')

class Migration(migrations.Migration):

    dependencies = [
        # Add any dependencies if needed
        ('customer', '0013_usersaving'),  # Example dependency
    ]

    operations = [
        # Example operation
        migrations.RunPython(create_user_login),
    ]
