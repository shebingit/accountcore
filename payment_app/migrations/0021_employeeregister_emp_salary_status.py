# Generated by Django 4.1 on 2023-02-25 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment_app', '0020_alter_employeesalary_empsalary_month'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeregister',
            name='emp_salary_status',
            field=models.IntegerField(default=0),
        ),
    ]