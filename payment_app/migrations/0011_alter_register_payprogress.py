# Generated by Django 4.1 on 2023-02-16 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0010_register_payprogress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='register',
            name='payprogress',
            field=models.IntegerField(default=10),
        ),
    ]