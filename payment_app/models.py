from django.db import models
from datetime import date



# Department Table handle all the department details
class Department(models.Model):
    department = models.CharField(max_length=255)
    dpt_Status = models.IntegerField(default=0)


class Dashboard_Register(models.Model):
    dsh_name = models.CharField(max_length=255,default='',null=True,blank=True)
    dsh_email = models.EmailField(max_length=255,default='email@gmail.com')
    dsh_phone = models.CharField(max_length=100,default='',null=True,blank=True)
    dsh_image = models.FileField(upload_to='profiles',default='')
    dsh_username = models.CharField(max_length=255,default='',null=True,blank=True)
    dsh_password = models.CharField(max_length=255,default='',null=True,blank=True)
    dsh_date = models.DateField(auto_now_add=True,null=True)
    active_status = models.IntegerField(default=0)


#Employee Table handle all the employee details
class EmployeeRegister(models.Model):
    empdept_id=models.ForeignKey(Department, on_delete=models.CASCADE, null=True,default='')
    acc_dashid=models.ForeignKey(Dashboard_Register, on_delete=models.CASCADE, null=True,default='')
    empdesignation=  models.CharField(max_length=255,default='')
    empfullName = models.CharField(max_length=255)
    empidreg = models.CharField(max_length=200,default='')
    empstate = models.CharField(max_length=200,default='')
    empPhone = models.CharField(max_length=15)
    empemail = models.EmailField()
    empdofj = models.DateField(auto_now_add=False,null=True)
    empconfirmsalary =  models.IntegerField(default=0,null=True)
    empfirst_salry= models.IntegerField(default=0)
    emptol_salary=models.IntegerField(default=0)
    emp_salary_status=models.IntegerField(default=0)
    emp_status = models.IntegerField(default=0)




# State table include all state and alocation ids
class Register_State(models.Model):
    allocate_dash=models.ForeignKey(Dashboard_Register, on_delete=models.CASCADE, null=True,default='')
    state_name= models.CharField(max_length=255,default='',null=True,blank=True)
    state_id= models.CharField(max_length=255,default='',null=True,blank=True)
    state_status= models.CharField(max_length=255,default='0',null=True,blank=True)
    allocateid= models.ForeignKey(EmployeeRegister, on_delete=models.CASCADE, null=True,default='')
    allocate_status= models.CharField(max_length=255,default='0',null=True,blank=True)



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




class Register(models.Model):
    dept_id=models.ForeignKey(Department, on_delete=models.CASCADE, null=True,default='')
    fullName = models.CharField(max_length=255)
    Phone = models.CharField(max_length=15)
    dofj = models.DateField()
    next_pay_date = models.DateField(auto_now_add=False,null=True)
    next_pat_amt =  models.IntegerField(default=0)
    refrence=  models.CharField(max_length=255)
    firstpay_id = models.IntegerField(default=0)
    fixed_intial_amt = models.IntegerField(default=0)
    regbalance_amt =  models.IntegerField(default=0)
    reg_payedtotal = models.IntegerField(default=0)
    regtotal_amt =  models.IntegerField(default=0)
    reg_status = models.IntegerField(default=0)
    payprogress = models.IntegerField(default=10)
    payment_status = models.IntegerField(default=0)
    reg_state=models.ForeignKey(Register_State, on_delete=models.CASCADE, null=True,default='')


class PaymentHistory(models.Model):
    reg_id=models.ForeignKey(Register, on_delete=models.CASCADE, null=True,default='')
    paydofj   = models.DateField(auto_now_add=False,null=True)
    head_name = models.CharField(max_length=255,default='')
    payintial_amt =  models.IntegerField(default=0)
    paybalance_amt =  models.IntegerField(default=0)
    paytotal_amt =  models.IntegerField(default=0)
    pay_status = models.IntegerField(default=0)
    admin_payconfirm = models.IntegerField(default=0)
    pay_state=models.ForeignKey(Register_State, on_delete=models.CASCADE, null=True,default='')




class Receipt_Data(models.Model):
    auth_fullname = models.CharField(max_length=255)
    auth_signature = models.FileField(upload_to='Receipt',default='')
    company_name = models.CharField(max_length=200,default='')
    company_address1 = models.CharField(max_length=200,default='')
    company_address2 = models.CharField(max_length=200,default='')
    company_address3 = models.CharField(max_length=200,default='')
    company_logo = models.FileField(upload_to='Receipt',default='')
    company_seal = models.FileField(upload_to='Receipt',default='')
    company_email = models.CharField(max_length=200,default='')
    company_site = models.CharField(max_length=200,default='')
    company_state = models.ForeignKey(Register_State, on_delete=models.CASCADE, null=True,default='')



class FixedExpence(models.Model):
    fixed_head_name = models.CharField(max_length=255)
    fixed_date = models.DateField(auto_now_add=False,null=True)
    fixed_amount = models.IntegerField(default=0)
    fixed_typ = models.IntegerField(default=0)
    fixed_dese = models.TextField(default='')
    fixed_status = models.IntegerField(default=0)
    fixed_state = models.ForeignKey(Register_State, on_delete=models.CASCADE, null=True,default='')


class IncomeExpence(models.Model):
    exin_head_name = models.CharField(max_length=255)
    exin_date = models.DateField(auto_now_add=False,null=True)
    exin_amount = models.IntegerField(default=0,null=True)
    exin_typ = models.IntegerField(default=0)
    exin_dese = models.TextField(default='')
    exin_status = models.IntegerField(default=0)
    exin_state = models.ForeignKey(Register_State, on_delete=models.CASCADE, null=True,default='')

class Company_Holidays(models.Model):
    ch_sdate = models.DateField(auto_now_add=False,null=True)
    ch_edate = models.DateField(auto_now_add=False,null=True)
    ch_no = models.IntegerField(default=0,null=True)
    ch_workno = models.IntegerField(default=0,null=True)
    ch_state = models.ForeignKey(Register_State, on_delete=models.CASCADE, null=True,default='')



   