# Generated by Django 4.1 on 2023-02-21 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0014_register_next_pat_amt'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='reg_payedtotal',
            field=models.IntegerField(default=0),
        ),
    ]
