# Generated by Django 4.2 on 2023-04-19 23:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('votations_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserVotation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_candidate', models.BooleanField(default=False)),
                ('is_substitute', models.BooleanField(default=False)),
                ('votes_received', models.IntegerField(default=0)),
                ('propossals', models.JSONField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('votation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='votations_app.votation')),
            ],
        ),
    ]
