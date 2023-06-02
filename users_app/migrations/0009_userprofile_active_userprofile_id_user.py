# Generated by Django 4.2 on 2023-05-17 03:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0008_userprofile_first_login"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="id_user",
            field=models.CharField(default="0", max_length=100, unique=True),
        ),
    ]
