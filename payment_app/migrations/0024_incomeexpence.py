# Generated by Django 4.1 on 2023-02-26 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0023_fixedexpence'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomeExpence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exin_head_name', models.CharField(max_length=255)),
                ('exin_date', models.DateField(null=True)),
                ('exin_amount', models.IntegerField(default=0)),
                ('exin_typ', models.IntegerField(default=0)),
                ('exin_dese', models.TextField(default='')),
                ('exin_status', models.IntegerField(default=0)),
            ],
        ),
    ]
