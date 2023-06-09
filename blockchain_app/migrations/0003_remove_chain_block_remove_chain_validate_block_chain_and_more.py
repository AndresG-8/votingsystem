# Generated by Django 4.2 on 2023-04-17 17:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('votations_app', '0001_initial'),
        ('blockchain_app', '0002_remove_transaction_amount_transaction_vote'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chain',
            name='block',
        ),
        migrations.RemoveField(
            model_name='chain',
            name='validate',
        ),
        migrations.AddField(
            model_name='block',
            name='chain',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='blockchain_app.chain'),
        ),
        migrations.AddField(
            model_name='chain',
            name='votation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='chain', to='votations_app.votation'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='block',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='blockchain_app.block'),
        ),
    ]
