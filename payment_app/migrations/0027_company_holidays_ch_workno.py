# Generated by Django 4.1 on 2023-03-01 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0026_company_holidays'),
    ]

    operations = [
        migrations.AddField(
            model_name='company_holidays',
            name='ch_workno',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
