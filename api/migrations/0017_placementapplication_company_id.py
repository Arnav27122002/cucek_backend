# Generated by Django 5.1.7 on 2025-04-14 13:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0016_remove_placementapplication_resume"),
    ]

    operations = [
        migrations.AddField(
            model_name="placementapplication",
            name="company_id",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="api.placementcompany",
            ),
            preserve_default=False,
        ),
    ]
