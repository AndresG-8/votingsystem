# Generated by Django 4.2 on 2023-05-13 05:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0005_userdetail_is_candidate_userdetail_is_substitute_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userdetail",
            name="profile_image",
            field=models.FileField(blank=True, null=True, upload_to="profile_images"),
        ),
    ]
