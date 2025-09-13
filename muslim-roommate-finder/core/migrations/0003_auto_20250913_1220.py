# core/migrations/000X_add_available_from.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_room_available_from.py'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='available_from',
            field=models.DateField(null=True, blank=True),
        ),
    ]
