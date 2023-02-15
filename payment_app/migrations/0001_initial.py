# Generated by Django 4.1 on 2023-02-15 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(max_length=255)),
                ('dpt_Status', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Register',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullName', models.CharField(max_length=255)),
                ('Phone', models.CharField(max_length=15)),
                ('dofj', models.DateField()),
                ('refrence', models.CharField(max_length=255)),
                ('reg_status', models.IntegerField(default=0)),
                ('dept_id', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='payment_app.department')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dofj', models.DateField()),
                ('intial_amt', models.IntegerField(default=0)),
                ('total_amt', models.IntegerField(default=0)),
                ('pay_status', models.IntegerField(default=0)),
                ('reg_id', models.ForeignKey(default='', null=True, on_delete=django.db.models.deletion.CASCADE, to='payment_app.register')),
            ],
        ),
    ]
