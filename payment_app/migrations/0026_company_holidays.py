# Generated by Django 4.1 on 2023-02-28 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0025_alter_incomeexpence_exin_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company_Holidays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ch_sdate', models.DateField(null=True)),
                ('ch_edate', models.DateField(null=True)),
                ('ch_no', models.IntegerField(default=0, null=True)),
            ],
        ),
    ]