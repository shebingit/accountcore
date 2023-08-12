# Generated by Django 4.1 on 2023-08-12 16:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0031_receipt_data_register_state_delete_expence_details_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard_Register',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dsh_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('dsh_email', models.EmailField(blank=True, default='', max_length=255, null=True)),
                ('dsh_phone', models.CharField(blank=True, default='', max_length=100, null=True)),
                ('dsh_image', models.FileField(default='', upload_to='profiles')),
                ('dsh_username', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('dsh_password', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('dsh_date', models.DateField(null=True)),
            ],
        ),
       
    ]
