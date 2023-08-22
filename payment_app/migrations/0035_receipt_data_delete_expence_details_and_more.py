# Generated by Django 4.1 on 2023-08-17 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0034_receipt_data_delete_expence_details_and_more'),
    ]

    operations = [
 
        migrations.AddField(
            model_name='employeeregister',
            name='acc_dashid',
            field=models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='payment_app.dashboard_register'),
        ),
        migrations.AddField(
            model_name='employeeregister',
            name='empstate',
            field=models.CharField(default='', max_length=200),
        ),
       
    ]