# Generated by Django 4.2 on 2023-05-10 19:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mempool_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mempooltransaction",
            name="is_taken",
            field=models.BooleanField(default=False),
        ),
    ]
