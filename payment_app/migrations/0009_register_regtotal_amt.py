# Generated by Django 4.1 on 2023-02-16 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0008_register_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='regtotal_amt',
            field=models.IntegerField(default=0),
        ),
    ]