# Generated by Django 4.2 on 2023-05-17 03:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mempool_app", "0004_remove_mempooltransaction_recipient_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="mempooltransaction",
            name="sender_signature",
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name="mempooltransaction",
            name="trx_data",
            field=models.CharField(max_length=500),
        ),
    ]
