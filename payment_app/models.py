from django.db import models
from datetime import date





class Department(models.Model):
    department = models.CharField(max_length=255)
    dpt_Status = models.IntegerField(default=0)



class Register(models.Model):
    dept_id=models.ForeignKey(Department, on_delete=models.CASCADE, null=True,default='')
    fullName = models.CharField(max_length=255)
    Phone = models.CharField(max_length=15)
    dofj = models.DateField()
    next_pay_date = models.DateField(auto_now_add=False,null=True)
    next_pat_amt =  models.IntegerField(default=0)
    refrence=  models.CharField(max_length=255)
    firstpay_id = models.IntegerField(default=0)
    regbalance_amt =  models.IntegerField(default=0)
    reg_payedtotal = models.IntegerField(default=0)
    regtotal_amt =  models.IntegerField(default=0)
    reg_status = models.IntegerField(default=0)
    payprogress = models.IntegerField(default=10)
    payment_status = models.IntegerField(default=0)

class PaymentHistory(models.Model):
    reg_id=models.ForeignKey(Register, on_delete=models.CASCADE, null=True,default='')
    paydofj   = models.DateField(auto_now_add=False,null=True)
    head_name = models.CharField(max_length=255,default='')
    payintial_amt =  models.IntegerField(default=0)
    paybalance_amt =  models.IntegerField(default=0)
    paytotal_amt =  models.IntegerField(default=0)
    pay_status = models.IntegerField(default=0)
    admin_payconfirm = models.IntegerField(default=0)


class EmployeeRegister(models.Model):
    empdept_id=models.ForeignKey(Department, on_delete=models.CASCADE, null=True,default='')
    empdesignation=  models.CharField(max_length=255,default='')
    empfullName = models.CharField(max_length=255)
    empidreg= models.CharField(max_length=200,default='')
    empPhone = models.CharField(max_length=15)
    empemail = models.EmailField()
    empdofj = models.DateField(auto_now_add=False,null=True)
    empconfirmsalary =  models.IntegerField(default=0)
    empfirst_salry= models.IntegerField(default=0)
    emptol_salary=models.IntegerField(default=0)
    emp_salary_status=models.IntegerField(default=0)
    emp_status = models.IntegerField(default=0)

class EmployeeSalary(models.Model):
    empreg_id=models.ForeignKey(EmployeeRegister, on_delete=models.CASCADE, null=True,default='')
    empsalary_month=models.CharField(max_length=55,default='')
    empslaray_date = models.DateField(auto_now_add=False,null=True)
    emppaid_amt =models.IntegerField(default=0)
    empfull_leave =models.IntegerField(default=0)
    emphalf_leave =models.IntegerField(default=0)
    empfull_leave_amt =models.IntegerField(default=0)
    emphalf_leave_amt =models.IntegerField(default=0)
    emp_delay =models.IntegerField(default=0)
    emp_delay_amt =models.IntegerField(default=0)
    emp_othe_head=models.CharField(max_length=100,default='')
    emp_other_amt =models.IntegerField(default=0)
    emp_other_damt=models.IntegerField(default=0)
    emp_paidstatus = models.IntegerField(default=0)


class Expence_Details(models.Model):
    exp_head_name = models.CharField(max_length=255)
    exp_date = models.DateField(auto_now_add=False,null=True)
    exp_amount = models.IntegerField(default=0)
    exp_typ = models.CharField(max_length=200,default='')
    exp_dese = models.TextField(default='')
    exp_status = models.IntegerField(default=0)



class FixedExpence(models.Model):
    fixed_head_name = models.CharField(max_length=255)
    fixed_date = models.DateField(auto_now_add=False,null=True)
    fixed_amount = models.IntegerField(default=0)
    fixed_typ = models.IntegerField(default=0)
    fixed_dese = models.TextField(default='')
    fixed_status = models.IntegerField(default=0)


class IncomeExpence(models.Model):
    exin_head_name = models.CharField(max_length=255)
    exin_date = models.DateField(auto_now_add=False,null=True)
    exin_amount = models.IntegerField(default=0,null=True)
    exin_typ = models.IntegerField(default=0)
    exin_dese = models.TextField(default='')
    exin_status = models.IntegerField(default=0)

class Company_Holidays(models.Model):
    ch_sdate = models.DateField(auto_now_add=False,null=True)
    ch_edate = models.DateField(auto_now_add=False,null=True)
    ch_no = models.IntegerField(default=0,null=True)
    ch_workno = models.IntegerField(default=0,null=True)

