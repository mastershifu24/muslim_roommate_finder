# core/migrations/000X_add_available_from.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', 'previous_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='available_from',
            field=models.DateField(null=True, blank=True),
        ),
    ]
