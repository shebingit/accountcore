from django.db import models
from datetime import date





class Department(models.Model):
    department = models.CharField(max_length=255)
    dpt_Status = models.CharField(max_length=50)



class Register(models.Model):
    dept_id=models.ForeignKey(Department, on_delete=models.CASCADE, null=True,default='')
    fullName = models.CharField(max_length=255)
    Phone = models.CharField(max_length=15)
    dofj = models.DateField()
    next_pay_date = models.DateField(auto_now_add=False,null=True)
    refrence=  models.CharField(max_length=255)
    firstpay_id = models.IntegerField(default=0)
    regbalance_amt =  models.IntegerField(default=0)
    regtotal_amt =  models.IntegerField(default=0)
    reg_status = models.IntegerField(default=0)
    payprogress = models.IntegerField(default=10)
    payment_status = models.IntegerField(default=0)

class PaymentHistory(models.Model):
    reg_id=models.ForeignKey(Register, on_delete=models.CASCADE, null=True,default='')
    paydofj   = models.DateField(auto_now_add=True,null=True)
    head_name = models.CharField(max_length=255,default='')
    payintial_amt =  models.IntegerField(default=0)
    paybalance_amt =  models.IntegerField(default=0)
    paytotal_amt =  models.IntegerField(default=0)
    pay_status = models.IntegerField(default=0)
    admin_payconfirm = models.IntegerField(default=0)

