from django.shortcuts import redirect, render
from django.contrib import messages
from payment_app.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import datetime
from datetime import datetime,timedelta
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from .utils import *
import calendar
from xhtml2pdf import pisa
from num2words import num2words
from django.db.models import Sum
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse

#===============comman views===============





#login Section
def login_page(request):
    return render(request, 'login.html')



def account_profile(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        user=User.objects.get(id=uid)
        
        return render(request,'account/account_profile.html',{'user':user})

    else:
            return redirect('/')




#login Authentication
def login_dashboard(request):
    if request.method=='POST':
            username=request.POST['uname']
            password=request.POST['psw']

            try:
                user=Dashboard_Register.objects.get(dsh_username=username,dsh_password=password)
            
            except Dashboard_Register.DoesNotExist:

                messages.info(request, 'Invalid Username  or  Password. Try Again.')
                return redirect('login_page')
            
            if user is not None:
                if user.active_status == 1:
                    request.session["admid"]=user.id
                    if 'admid' in request.session:
                        if request.session.has_key('admid'):
                            admid = request.session['admid']
                        else:
                            return redirect('/')
                        
                        admin_DHB=Dashboard_Register.objects.get(id=admid)
                        success_msg = 'Authentication Success!'

                       
                        new_reg=Register.objects.filter(reg_status=0).count()  #Geting the new OJT registration count

                        common_data = nav_data(request) # calling for navbar datas

                        data_check = income_expence_check(request)

                        print(data_check)

                        otj_reg = Register.objects.all().count()
                        emp_reg = EmployeeRegister.objects.all().count()
                        state_reg = Register_State.objects.filter(allocate_status=1).count()

                        content = {'admin_DHB':admin_DHB,
                                   'success_msg':success_msg,
                                   'new_reg':new_reg,
                                   'otj_reg':otj_reg,
                                   'emp_reg':emp_reg,
                                   'state_reg':state_reg
                                   
                                   }
                        # Merge the two dictionaries
                        content = {**content, **common_data}

                        return render(request,'Admin/Admin_dashboard.html',content)
                    
                    else:
                        return redirect('/')
                else:
                    request.session["uid"]=user.id
                   
                    if request.session.has_key('uid'):
                        uid = request.session['uid']

                    else:
                        return redirect('/')
                    
                        
                    account_DHB=Dashboard_Register.objects.get(id=uid)
                    acc_state = Register_State.objects.get(allocate_dash=account_DHB)
                    #-----------------------------------------------------------------
                
                    cur_date=datetime.now().date()
                    fr_date=datetime(cur_date.year, cur_date.month, 1).date()
                    last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
                    to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 


                    reg=Register.objects.filter(reg_status=1,reg_state=acc_state )
                    reg_count=Register.objects.filter(reg_state=acc_state).count()
                    emp_reg_count = EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()
        
                    success_msg = 'Authentication Success!'
                    pay_pending_count=Register.objects.filter(Q(payment_status=0) | Q(payment_status=2),next_pay_date__lte=cur_date,reg_status=1,reg_state=acc_state).order_by('-next_pay_date')
                    pay_count=Register.objects.filter(Q(payment_status=0) | Q(payment_status=2),next_pay_date__lte=cur_date,reg_status=1,reg_state=acc_state).count()
       
                    common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       

                    content={'account_DHB':account_DHB,'cur_date':cur_date,
                            'emp_reg_count':emp_reg_count,
                            'reg_count':reg_count,
                            'pay_count':pay_count,
                            'pay_pending_count':pay_pending_count,
                             'success_msg':success_msg,
                            'reg':reg,'acc_state':acc_state}
                    
                    content = {**content, **common_accdash_data}
                    
                    return render(request,'account/dashboard.html',content)
                    
            else:
                messages.info(request, 'Invalid Username  or  Password. Try Again.')
                return redirect('login_page')
    else:
            return redirect('login_page')





# ==============================Account Module Section============================


def dashboard(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid)
        acc_state = Register_State.objects.get(allocate_dash=account_DHB)
        #-------------------------------------------------
        

        reg=Register.objects.filter(reg_status=1,reg_state=acc_state )
        reg_count=Register.objects.filter(reg_state=acc_state).count()
        emp_reg_count = EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()
        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

       

        if request.method == 'POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']

            if sdate and edate:

                pay_pending_count=Register.objects.filter(Q(payment_status=0) | Q(payment_status=2),next_pay_date__gte=sdate,next_pay_date__lte=edate,reg_status=1,reg_state=acc_state).order_by('-next_pay_date')
                pay_count=Register.objects.filter(Q(payment_status=0) | Q(payment_status=2),next_pay_date__gte=sdate,next_pay_date__lte=edate,reg_status=1,reg_state=acc_state).count()
            else:
                return redirect('dashboard')
        else:

            pay_pending_count=Register.objects.filter(Q(payment_status=0) | Q(payment_status=2),next_pay_date__lte=cur_date,reg_status=1,reg_state=acc_state).order_by('-next_pay_date')
            pay_count=Register.objects.filter(Q(payment_status=0) | Q(payment_status=2),next_pay_date__lte=cur_date,reg_status=1,reg_state=acc_state).count()
       
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       

        content={'account_DHB':account_DHB,'cur_date':cur_date,
                 'emp_reg_count':emp_reg_count,
                'reg_count':reg_count,
                'pay_count':pay_count,
                'pay_pending_count':pay_pending_count,
                'reg':reg,'acc_state':acc_state}
        
        content = {**content, **common_accdash_data}
        
        return render(request,'account/dashboard.html',content)
    
    else:
        return redirect('/')
    

# Account Profile------------------------

def account_profile(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
       
        #-------------------------------------------------

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        
        return render(request,'account/account_profile.html',content)

    else:
            return redirect('/')


# Account Details -----------------------------------------


def profile_account_details_save(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch

        if request.method == 'POST':
            
            account_DHB.dsh_name = request.POST['fname']
            account_DHB.dsh_email = request.POST['email']
            account_DHB.dsh_username = request.POST['uname'] 
            if  request.FILES.get('profile_pic'):
                account_DHB.dsh_image = request.FILES.get('profile_pic')
            else:
                account_DHB.dsh_image = account_DHB.dsh_image 
            account_DHB.save()

            success_msg= 'Success! Profile Data Updated Successfully'
            account_DHB=Dashboard_Register.objects.get(id=uid)

            content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    success_msg:success_msg}
        
        else:
            error_msg='Oops! Something Went Wrong'

            content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'error_msg':error_msg
                    }
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}

        return render(request,'account/account_profile.html',content)

    else:
            return redirect('/')


# Account Password ----------------------------------------

def account_password_change(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        
        if request.method=='POST':

            oldpassword=request.POST['oldpsw']
            newpassword=request.POST['newpsw']
            confpassword=request.POST['confpsw']

            if newpassword != confpassword:

                error_msg = 'Opps! New Password and Confirm Password not maching'

                content={'account_DHB':account_DHB,
                            'error_msg':error_msg,
                            'acc_state':acc_state,
                 }
                
                common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  

                content = {**content, **common_accdash_data}

                return render(request,'account/account_profile.html',content)

           
            if oldpassword == account_DHB.dsh_password:

                account_DHB.dsh_password=newpassword
                account_DHB.save()

                success_msg= 'Success! Password Updated Successfully'
                account_DHB=Dashboard_Register.objects.get(id=uid)

                content={'account_DHB':account_DHB,
                        'success_msg':success_msg,
                        'acc_state':acc_state,
                    }
            
            else:

               
                error_msg = 'Opps! Old Password and New Password not maching'
                content={'account_DHB':account_DHB,
                            'error_msg':error_msg,
                            'acc_state':acc_state,
                 }
               

        else:
            error_msg = 'Opps! Something Went Wrong'
            content={'account_DHB':account_DHB,
                'error_msg':error_msg,
                'acc_state':acc_state,
                 } 
                 
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  

        content = {**content, **common_accdash_data}

        return render(request,'account/account_profile.html',content)
   
    else:
        return redirect('/')



#=============================================== OJT Section ========================================================

# OJT register -------------------------------

def Register_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        depart = Department.objects.filter(dpt_Status=1)
        #-------------------------------------------------

        # saveing the employee details

        if request.method =='POST':
            reg=Register()
            reg.fullName=request.POST['name']
            reg.Phone=request.POST['phno']
            reg.dofj=request.POST['dfj']
            reg.refrence=request.POST['refby']
            intial_amt=int(request.POST['init_amunt'])
            total_amt=int(request.POST['tot_amount'])
            reg.fixed_intial_amt= int(request.POST['fixedinit_amunt'])
            cal=int(request.POST['fixedinit_amunt'])
          
    
            reg.regtotal_amt=total_amt
            reg.dept_id=Department.objects.get(id=request.POST['dept'])
            next_date=request.POST['nxtpdof']

            if next_date:
                reg.next_pay_date=request.POST['nxtpdof']

            else:
               
                current_date = request.POST['dfj']
                current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
                # Calculate the date after 30 days
                if intial_amt >= cal:
                    after_days = current_date + timedelta(days=30)
                   
                # Calculate the date after 15 days
                else:
                     after_days = current_date + timedelta(days=15)
                   
                reg.next_pay_date=after_days
            
            reg.reg_state = acc_state

            reg.save()

            payhis=PaymentHistory()
            payhis.head_name='Initial Payment'
            payhis.paydofj=(request.POST['dfpayment'])
            payhis.payintial_amt=intial_amt
            payhis.paytotal_amt=total_amt
            
            payhis.pay_status=1
            payhis.reg_id=reg
            payhis.pay_state = acc_state
            payhis.save()

            reg.firstpay_id=payhis.id
            reg.save()

            success_msg="Success! You have saved OJT tainee details."

            reg=Register.objects.filter(reg_state=acc_state)
            reg_count=Register.objects.filter(reg_state=acc_state).count()
            payhis=PaymentHistory.objects.filter(reg_id__in=reg)


            content={'account_DHB':account_DHB,
                    'depart':depart,
                    'payhis':payhis,
                    'reg':reg,
                    'reg_count':reg_count,
                    'acc_state':acc_state,
                    'success_msg':success_msg}

        else:
        
            reg=Register.objects.filter(reg_state=acc_state).order_by('-dofj')
            reg_count=Register.objects.filter(reg_state=acc_state).count()
            payhis=PaymentHistory.objects.filter(reg_id__in=reg)

                

            content={'account_DHB':account_DHB,
                    'depart':depart,
                    'payhis':payhis,
                    'reg':reg,
                    'reg_count':reg_count,
                    'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}

        return render(request,'account/Register_form.html',content)
    else:
        return redirect('/')


# OJT Registration edit ----------------------
def register_edit(request,pk):
  

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------

        # Edit saveing the employee details

        if request.method =='POST':

            reg=Register.objects.get(id=pk)
            
            reg.fullName=request.POST['name']
            reg.Phone=request.POST['phno']
            if request.POST['dfj']:
                reg.dofj=request.POST['dfj']
            else:
                 reg.dofj= reg.dofj
            reg.refrence=request.POST['refby']
            intial_amt=int(request.POST['init_amunt'])
            total_amt=int(request.POST['tot_amount'])
            reg.fixed_intial_amt= int(request.POST['fixedinit_amunt'])
            cal=int(request.POST['fixedinit_amunt'])
          
    
            reg.regtotal_amt=total_amt
            reg.dept_id=Department.objects.get(id=request.POST['dept'])
            next_date=request.POST['nxtpdof']

            if next_date:
                reg.next_pay_date=request.POST['nxtpdof']

            else:
               
                current_date = request.POST['dfj']
                current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
                # Calculate the date after 30 days
                if intial_amt >= cal:
                    after_days = current_date + timedelta(days=30)
                   
                # Calculate the date after 15 days
                else:
                     after_days = current_date + timedelta(days=15)
                   
                reg.next_pay_date=after_days
            
            reg.reg_state = acc_state

            reg.save()

            payhis=PaymentHistory.objects.get(reg_id_id=reg.id,admin_payconfirm=0)
            payhis.head_name='Initial Payment'

            if request.POST['dfpayment']:
                payhis.paydofj=request.POST['dfpayment']
            else:
                payhis.paydofj=payhis.paydofj

            payhis.payintial_amt=intial_amt
            payhis.paytotal_amt=total_amt
            
            payhis.pay_status=1
            payhis.reg_id=reg
            payhis.pay_state = acc_state
            payhis.save()

            reg.firstpay_id=payhis.id
            reg.save()

            success_msg="Success! You have edit OJT tainee details."
            reg=Register.objects.get(id=pk)
            payhis=PaymentHistory.objects.get(reg_id_id=reg.id,admin_payconfirm=0)
        
            depart = Department.objects.filter(dpt_Status=1)
        
        

            if payhis.admin_payconfirm == 0:
            
                content={'account_DHB':account_DHB,
                        'depart':depart,
                        'payhis':payhis,
                        'reg':reg,
                        'success_msg':success_msg,
                        'acc_state':acc_state}


        else:

            reg=Register.objects.get(id=pk)

            try:
                payhis=PaymentHistory.objects.get(reg_id_id=reg.id,admin_payconfirm=0)
            except PaymentHistory.DoesNotExist:
                payhis=PaymentHistory.objects.get(reg_id_id=reg.id,admin_payconfirm=1)
        
            depart = Department.objects.filter(dpt_Status=1)
        
        

            content={'account_DHB':account_DHB,
                        'depart':depart,
                        'payhis':payhis,
                        'reg':reg,
                        'acc_state':acc_state}
            
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       
            
        content = {**content, **common_accdash_data}

        return render(request,'account/register_edit_form.html',content)
           
           
    else:
        return redirect('/')

# OJT Register Details Edit------------------

def register_edit_details(request,pk):
  

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------

        # Edit saveing the employee details

        if request.method =='POST':

            reg=Register.objects.get(id=pk)
            
            reg.fullName=request.POST['name']
            reg.Phone=request.POST['phno']
            if request.POST['dfj']:
                reg.dofj=request.POST['dfj']
            else:
                 reg.dofj= reg.dofj
            reg.refrence=request.POST['refby']

            reg.dept_id=Department.objects.get(id=request.POST['dept'])
            next_date=request.POST['nxtpdof']

            if next_date:
                reg.next_pay_date=request.POST['nxtpdof']

            else:
                reg.next_pay_date = reg.next_pay_date
                
            reg.reg_state = acc_state

            reg.save()


            success_msg="Success! You have edit OJT tainee details."
            reg=Register.objects.get(id=pk)
            
        
            depart = Department.objects.filter(dpt_Status=1)
 
            content={'account_DHB':account_DHB,
                        'depart':depart,                      
                        'reg':reg,
                        'success_msg':success_msg,
                        'acc_state':acc_state}
        else:

            reg=Register.objects.get(id=pk)
            depart = Department.objects.filter(dpt_Status=1)
        
        

            content={'account_DHB':account_DHB,
                        'depart':depart,
                        'reg':reg,
                        'acc_state':acc_state}
            
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       
            
        content = {**content, **common_accdash_data}

        return render(request,'account/register_editDetails_form.html',content)
           
           
    else:
        return redirect('/')
# OJT Register remove ------------------------
def remove(request,pk):
        
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        depart = Department.objects.filter(dpt_Status=1)
        #-------------------------------------------------

        try:
            reg=Register.objects.get(id=pk)
            reg.delete()
            error_msg="Opps! You have removed OJT trainee details."
        except Register.DoesNotExist:
            error_msg="Opps!  OJT trainee details Does not exist."

        reg=Register.objects.filter(reg_state=acc_state).order_by('-dofj')
        reg_count=Register.objects.filter(reg_state=acc_state).count()
        payhis=PaymentHistory.objects.filter(reg_id__in=reg)

        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas            

        content={'account_DHB':account_DHB,
                    'depart':depart,
                    'payhis':payhis,
                    'reg':reg,
                    'reg_count':reg_count,
                    'acc_state':acc_state,
                    'error_msg':error_msg}
        
        content = {**content, **common_accdash_data}

        return render(request,'account/Register_form.html',content)
    
    else:
        return redirect('/')



#================================================= Employee Section  ===================================================

# Employee register ------------------
def emp_Register_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        
        #-------------------------------------------------
        depart= Department.objects.all()
        emp_reg=EmployeeRegister.objects.filter(empstate=acc_state.state_name)
        emp_reg_count=EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()

       
        if request.method =='POST':
            emp_reg=EmployeeRegister()
            emp_reg.empfullName=request.POST['emp_Name']
            emp_reg.empdept_id=Department.objects.get(id=request.POST['emp_dept'])
            emp_reg.empdofj=request.POST['emp_dfj']
            emp_reg.empdesignation=request.POST['emp_desig'].upper()
            emp_reg.empidreg=request.POST['emp_id'].upper()
            emp_reg.empconfirmsalary=int(request.POST['emp_sal'])
            emp_reg.empstate=request.POST['emp_state']
            emp_reg.emp_status=1
            emp_reg.emp_salary_status=1

            emp_reg.save()
            success_msg='Success! Employee registration completed.'
        
       
            emp_reg=EmployeeRegister.objects.filter(empstate=acc_state.state_name)
            emp_reg_count=EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()

            content={'account_DHB':account_DHB,
                     'depart':depart,
                    'emp_reg':emp_reg,
                    'emp_reg_count':emp_reg_count,
                    'acc_state':acc_state,'success_msg':success_msg}
    
    
        content={'account_DHB':account_DHB,
                    'emp_reg':emp_reg,
                     'depart':depart,
                    'emp_reg_count':emp_reg_count,
                    'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/Employee_Register.html',content)
    
    else:
        return redirect('/')
    

#Employee Edit ---------------
def employee_reg_edit(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
        depart= Department.objects.filter(dpt_Status=1)
        
        emp_reg=EmployeeRegister.objects.get(id=pk)

        if request.method =='POST':
          
            emp_reg.empfullName=request.POST['emp_Name']
            emp_reg.empdept_id=Department.objects.get(id=request.POST['emp_dept'])
            if request.POST['emp_dfj']:
                emp_reg.empdofj=request.POST['emp_dfj']
            else:
                emp_reg.empdofj=emp_reg.empdofj
            emp_reg.empdesignation=request.POST['emp_desig'].upper()
            emp_reg.empidreg=request.POST['emp_id'].upper()
            emp_reg.empconfirmsalary=int(request.POST['emp_sal'])
            emp_reg.empstate=request.POST['emp_state']
            emp_reg.emp_status=1
            emp_reg.emp_salary_status=1

            emp_reg.save()
            emp_reg=EmployeeRegister.objects.get(id=pk)

            success_msg='Success! Employee details edited.'
            content={'account_DHB':account_DHB,
                    'emp_reg':emp_reg,
                     'depart':depart,
                    'acc_state':acc_state,'success_msg':success_msg}
        else:

    
            content={'account_DHB':account_DHB,
                        'emp_reg':emp_reg,
                        'depart':depart,
                        'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/Employee_Register_edit.html',content)
        
    else:
        return redirect('/')  


# Employee delete ---------------
def emp_reg_delete(request,pk):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
        depart= Department.objects.filter(dpt_Status=1)
        emp_reg=EmployeeRegister.objects.get(id=pk)
       
        emp_reg.delete()

        error_msg='Opps! Employee details removed.'
        emp_reg=EmployeeRegister.objects.filter(empstate=acc_state.state_name)
        emp_reg_count=EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()

        content={'account_DHB':account_DHB,
                    'emp_reg':emp_reg,
                     'depart':depart,
                     'emp_reg_count':emp_reg_count,
                    'acc_state':acc_state,'error_msg':error_msg}
        
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/Employee_Register.html',content)
    
    else:
        return redirect('/')





# ================================================== Department Section ==================================================

# Department register ----------------
def department_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch

        #-------------------------------------------------

        if request.method =='POST':
            
            if request.POST['dept_id']:
                dept=Department.objects.get(id=int( request.POST['dept_id']))
                dept.department=request.POST['dept_name'].upper()
                dept.save()
                success_msg='Success! Department edited.'
            else:
                dept=Department()
                dept.department=request.POST['dept_name'].upper()
                dept.dpt_Status=1
                dept.save()
                success_msg='Success! Department added.'
            
            dept=Department.objects.all()
            dept_count=Department.objects.all().count()
            content={'account_DHB':account_DHB,
                    'dept':dept,
                    'dept_count':dept_count,
                    'acc_state':acc_state,'success_msg':success_msg}
            
            common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas    
        
            content = {**content, **common_accdash_data}
            return render(request,'account/Department_form.html',content)
           
        else:

            dept=Department.objects.all()
            dept_count=Department.objects.all().count()
            content={'account_DHB':account_DHB,
                    'dept':dept,
                    'dept_count':dept_count,
                    'acc_state':acc_state}
            
            common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       
        
            content = {**content, **common_accdash_data}
            return render(request,'account/Department_form.html',content)
       
    else:
        return redirect('/')

# Department edit----------------
def edit_dept(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch

        #-------------------------------------------------
        
        dept_edit=Department.objects.get(id=pk)

        dept=Department.objects.all()
        dept_count=Department.objects.all().count()
        content={'account_DHB':account_DHB,
                    'dept':dept,
                    'dept_count':dept_count,
                    'acc_state':acc_state,'dept_edit':dept_edit}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/Department_form.html',content)
    
    else:
        return redirect('/')         


# Department Delete -------------
def remove_dept(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch

        #-------------------------------------------------
        
        dept=Department.objects.get(id=pk)
        dept.delete()
        error_msg = 'Opps! Department Removed'
        dept=Department.objects.all()
        dept_count=Department.objects.all().count()
        content={'account_DHB':account_DHB,
                    'dept':dept,
                    'dept_count':dept_count,
                    'acc_state':acc_state,'error_msg':error_msg}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/Department_form.html',content)
    
    else:
        return redirect('/')





        
# OJT Payment delete ---------------
def payhis_remove(request,pk):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------
        
        payhis=PaymentHistory.objects.get(id=pk)
        ojt_reg=Register.objects.filter(reg_status=1,payment_status=0,reg_state=acc_state)
        ojt_count=Register.objects.filter(reg_status=1,payment_status=0,reg_state=acc_state).count()
        pay_history = PaymentHistory.objects.filter(reg_id__in=ojt_reg,admin_payconfirm=0)


        if payhis.admin_payconfirm == 0:

            payhis.delete()
            error_msg='Opps! One Payment is deleted'
    
        else:
            error_msg='Sorry! The Payment is already approved'


        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'ojt_reg':ojt_reg,
                    'ojt_count':ojt_count,
                    'pay_history':pay_history,
                    'error_msg':error_msg
                   }
        
        content = {**content, **common_accdash_data}

        return render(request,'account/payment_add_page.html',content)
    
    else:
        return redirect('/')



# ======================== All View section =====================================

#OJT List--------------------
def OJT_list_view(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        if request.method == 'POST':

            sdate= request.POST['start_date']
            edate= request.POST['end_date']

            if sdate and edate:

                reg_ojt= Register.objects.filter(reg_state=acc_state,dofj__gte=sdate,dofj__lte=edate)
                reg_ojt_count= Register.objects.filter(reg_state=acc_state,dofj__gte=sdate,dofj__lte=edate).count()

            else:
                reg_ojt= Register.objects.filter(reg_state=acc_state)
                reg_ojt_count= Register.objects.filter(reg_state=acc_state).count()


        else:

            reg_ojt= Register.objects.filter(reg_state=acc_state)
            reg_ojt_count= Register.objects.filter(reg_state=acc_state).count()

        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'reg_ojt':reg_ojt,
                    'reg_ojt_count':reg_ojt_count
                   }
        
        content = {**content, **common_accdash_data}

        return render(request,'account/OJT_list_page.html',content)

    else:
        return redirect('/')

#OJT Payment track view-----
# ------------Payments History--------

def pyments_history(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        # Current month start date and End date
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 


        reg=Register.objects.filter(reg_state=acc_state)


        if request.method == 'POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']

            if sdate and edate:

                payhistory=PaymentHistory.objects.filter(reg_id__in=reg,paydofj__gte=sdate,paydofj__lte=edate).order_by('-id')
                payhistory_count=PaymentHistory.objects.filter(reg_id__in=reg,paydofj__gte=sdate,paydofj__lte=edate).count()

                ojt_approve_amt=PaymentHistory.objects.filter(reg_id__in=reg,admin_payconfirm=1,paydofj__gte=sdate,paydofj__lte=edate).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
                ojt_approve_count=PaymentHistory.objects.filter(reg_id__in=reg,admin_payconfirm=1,paydofj__gte=sdate,paydofj__lte=edate).count()

                ojt_pending_amt=PaymentHistory.objects.filter(reg_id__in=reg,admin_payconfirm=0,paydofj__gte=sdate,paydofj__lte=edate).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
                ojt_pending_count=PaymentHistory.objects.filter(reg_id__in=reg,admin_payconfirm=0,paydofj__gte=sdate,paydofj__lte=edate).count()

                

                content={'account_DHB':account_DHB,
                            'acc_state':acc_state,
                            'payhistory':payhistory,
                            'payhistory_count':payhistory_count,
                            'ojt_approve_amt':ojt_approve_amt,
                            'ojt_approve_count':ojt_approve_count,
                            'ojt_pending_amt':ojt_pending_amt,
                            'ojt_pending_count':ojt_pending_count
                        }
                
            else:

                return redirect('pyments_history')

        else:

            payhistory=PaymentHistory.objects.filter(reg_id__in=reg,paydofj__gte=fr_date,paydofj__lte=to_date).order_by('-id')
            payhistory_count=PaymentHistory.objects.filter(reg_id__in=reg,paydofj__gte=fr_date,paydofj__lte=to_date).count()

            ojt_approve_amt=PaymentHistory.objects.filter(reg_id__in=reg,admin_payconfirm=1,paydofj__gte=fr_date,paydofj__lte=to_date).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
            ojt_approve_count=PaymentHistory.objects.filter(reg_id__in=reg,admin_payconfirm=1,paydofj__gte=fr_date,paydofj__lte=to_date).count()

            ojt_pending_amt=PaymentHistory.objects.filter(reg_id__in=reg,admin_payconfirm=0,paydofj__gte=fr_date,paydofj__lte=to_date).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
            ojt_pending_count=PaymentHistory.objects.filter(reg_id__in=reg,admin_payconfirm=0,paydofj__gte=fr_date,paydofj__lte=to_date).count()

              

            content={'account_DHB':account_DHB,
                        'acc_state':acc_state,
                        'payhistory':payhistory,
                        'payhistory_count':payhistory_count,
                        'ojt_approve_amt':ojt_approve_amt,
                        'ojt_approve_count':ojt_approve_count,
                        'ojt_pending_amt':ojt_pending_amt,
                        'ojt_pending_count':ojt_pending_count
                    }
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas    

        content = {**content, **common_accdash_data}

        return render(request,'account/payments_history.html',content)

    else:
        return redirect('/')

def pyments_status_view(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        cur_date=datetime.now().date() # Current date 

        if request.method == 'POST':

            sdate= request.POST['start_date']
            edate= request.POST['end_date']

            if sdate and sdate :

                if pk == 0:
                    reg=Register.objects.filter(dofj__gte=sdate,dofj__lte=edate,reg_state=acc_state,payment_status=0)
                    ojt_count=Register.objects.filter(dofj__gte=sdate,dofj__lte=edate,reg_state=acc_state,payment_status=0).count()

                elif pk == 1:

                    reg=Register.objects.filter(dofj__gte=sdate,dofj__lte=edate,reg_state=acc_state,payment_status=1)
                    ojt_count=Register.objects.filter(dofj__gte=sdate,dofj__lte=edate,reg_state=acc_state,payment_status=1).count()

                else:
                    reg=Register.objects.filter(dofj__gte=sdate,dofj__lte=edate,reg_state=acc_state,payment_status=2)
                    ojt_count=Register.objects.filter(dofj__gte=sdate,dofj__lte=edate,reg_state=acc_state,payment_status=2).count()

            
            else:
                return redirect('pyments_status_view',pk)
        

        else:

            if pk == 0:
                reg=Register.objects.filter(reg_state=acc_state,payment_status=0)
                ojt_count=Register.objects.filter(reg_state=acc_state,payment_status=0).count()

            elif pk == 1:

                reg=Register.objects.filter(reg_state=acc_state,payment_status=1)
                ojt_count=Register.objects.filter(reg_state=acc_state,payment_status=1).count()

            else:
                reg=Register.objects.filter(reg_state=acc_state,payment_status=2)
                ojt_count=Register.objects.filter(reg_state=acc_state,payment_status=2).count()


        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas    
        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'reg':reg,
                    'ojt_count':ojt_count,
                    'pk':pk,'cur_date':cur_date
                   }

        content = {**content, **common_accdash_data}

        return render(request,'account/payments_status_view.html',content)

    else:
        return redirect('/')

#Single User Payments Viev

def singleuser_details(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        reg=Register.objects.get(id=pk,reg_state=acc_state)
        payhis=PaymentHistory.objects.filter(reg_id_id=reg.id,pay_state=acc_state)
        ojt_count = PaymentHistory.objects.filter(reg_id_id=reg.id,pay_state=acc_state).count()
       
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas    

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'reg':reg,
                    'ojt_count':ojt_count,
                    'payhis':payhis
                   }

        content = {**content, **common_accdash_data}

        return render(request,'account/SingleUser_payments.html',content)

    else:
        return redirect('/')  
    

def user_active_reactive(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        
        reg=Register.objects.get(id=pk)
        if reg.payment_status == 0:
           reg.payment_status = 2
        elif reg.payment_status == 2: 
            reg.payment_status = 0 
        reg.save()      
        
        payhis=PaymentHistory.objects.filter(reg_id_id=reg.id)
        ojt_count = PaymentHistory.objects.filter(reg_id_id=reg.id).count()
       
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas    

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'reg':reg,
                    'ojt_count':ojt_count,
                    'payhis':payhis
                   }

        content = {**content, **common_accdash_data}

        return render(request,'account/SingleUser_payments.html',content)
    else:
        return redirect('/')
    

def delete_user(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #----------------------------------------------------------------

        reg=Register.objects.get(id=pk)
        reg.payment_status=2
        if reg.reg_status == 2:
            reg.reg_status=1
        elif reg.reg_status == 1:
            reg.reg_status=2
        reg.save()

        return redirect('singleuser_details',reg.id)
       
    else:
        return redirect('/')


def previous_data(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #----------------------------------------------------------------
        try:
            pk=int(pk-1)
            reg=Register.objects.get(id=pk,reg_state=acc_state)
        
        except Register.DoesNotExist:
            reg=Register.objects.filter(reg_status=1,reg_state=acc_state).first()
           
        
        payhis=PaymentHistory.objects.filter(reg_id_id=reg.id,pay_state=acc_state)
        ojt_count = PaymentHistory.objects.filter(reg_id_id=reg.id,pay_state=acc_state).count()
       
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas    

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'reg':reg,
                    'ojt_count':ojt_count,
                    'payhis':payhis
                   }

        content = {**content, **common_accdash_data}
        return render(request,'account/SingleUser_payments.html',content)

    else:
        return redirect('/')
        
    

def next_data(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #----------------------------------------------------------------
        
        try:
            pk=int(pk+1)
            reg=Register.objects.get(id=pk,reg_state=acc_state)

        except Register.DoesNotExist:
            reg=Register.objects.filter(reg_status=1,reg_state=acc_state).last()
           
        
        payhis=PaymentHistory.objects.filter(reg_id_id=reg.id,pay_state=acc_state)
        ojt_count = PaymentHistory.objects.filter(reg_id_id=reg.id,pay_state=acc_state).count()
       
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas    

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'reg':reg,
                    'ojt_count':ojt_count,
                    'payhis':payhis
                   }

        content = {**content, **common_accdash_data}
        return render(request,'account/SingleUser_payments.html',content)
    else:
        return redirect('/')



#Employees List ------------
def employee_list_view(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        if request.method == 'POST':

            sdate= request.POST['start_date']
            edate= request.POST['end_date']

            if sdate and edate:

                reg_emp= EmployeeRegister.objects.filter(empstate=acc_state.state_name,empdofj__gte=sdate,empdofj__lte=edate)
                reg_emp_count= EmployeeRegister.objects.filter(empstate=acc_state.state_name,empdofj__gte=sdate,empdofj__lte=edate).count()

            else:
                reg_emp= EmployeeRegister.objects.filter(empstate=acc_state.state_name)
                reg_emp_count= EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()


        else:

            reg_emp= EmployeeRegister.objects.filter(empstate=acc_state.state_name)
            reg_emp_count= EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()

        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'reg_emp':reg_emp,
                    'reg_emp_count':reg_emp_count
                   }
        
        content = {**content, **common_accdash_data}

        return render(request,'account/employee_list_page.html',content)

    else:
        return redirect('/')


#Employee Allocate List--------

def allocate_list(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        if request.method == 'POST':

            if pk == 4:

                try:
                    state_names = Register_State.objects.get(id=int(request.POST['search_select'])) 
                    selected_ojt = request.POST.getlist('select_OJT')

                    for i in selected_ojt:
                        ojt=Register.objects.get(id=i)
                        ojt.reg_state=state_names
                        ojt.save()

                        payhis=PaymentHistory.objects.filter(reg_id=ojt)
                        for j in payhis:
                            payment=PaymentHistory.objects.get(id=j.id)
                            payment.pay_state=state_names
                            payment.save()

                    
                    reg_ojt= Register.objects.filter(reg_state=None)
                    reg_ojt_count= Register.objects.filter(reg_state=None).count()

                except Register_State.DoesNotExist:
                    return redirect('allocate_list',9)
           

            elif pk == 5:

                try:
                    state_names = Register_State.objects.get(id=int(request.POST['search_select'])) 
                    selected_employees = request.POST.getlist('select_emp')

                    for i in selected_employees:
                        emp=EmployeeRegister.objects.get(id=i)
                        emp.empstate=state_names.state_name
                        emp.acc_dashid=account_DHB
                        emp.save()
                    
                    reg_emp= EmployeeRegister.objects.filter(empstate='')
                    reg_emp_count= EmployeeRegister.objects.filter(empstate='').count()

                except Register_State.DoesNotExist:
                    return redirect('allocate_list',9)
                
            elif pk == 6:

                try:
                    state_names = Register_State.objects.get(id=int(request.POST['search_select'])) 
                    selected_inex = request.POST.getlist('search_inex')

                    for i in selected_inex:
                        inexp=IncomeExpence.objects.get(id=i)
                        inexp.exin_state=state_names
                        inexp.save()
                    
                    inex= IncomeExpence.objects.filter(exin_state=None)
                    inex_count= IncomeExpence.objects.filter(exin_state=None).count()

                except Register_State.DoesNotExist:
                    return redirect('allocate_list',9)

            
            elif pk == 7:

                try:
                    state_names = Register_State.objects.get(id=int(request.POST['search_select'])) 
                    selected_fix = request.POST.getlist('select_fix')

                    for i in selected_fix:
                        fix=FixedExpence.objects.get(id=i)
                        fix.fixed_state=state_names
                        fix.save()
                    
                    fxex= FixedExpence.objects.filter(fixed_state=None)
                    fxex_count= FixedExpence.objects.filter(fixed_state=None).count()


                except Register_State.DoesNotExist:
                    return redirect('allocate_list',9)

            elif pk == 8:

                try:
                    state_names = Register_State.objects.get(id=int(request.POST['search_select'])) 
                    selected_holi = request.POST.getlist('select_holiday')

                    for i in selected_holi:
                        holidays=Company_Holidays.objects.get(id=i)
                        holidays.ch_state=state_names
                        holidays.save()
                    
                    holid= Company_Holidays.objects.filter(ch_state=None)
                    holid_count= Company_Holidays.objects.filter(ch_state=None).count()


                except Register_State.DoesNotExist:
                    return redirect('allocate_list',9)
           
        

        reg_emp= EmployeeRegister.objects.filter(empstate='')
        reg_emp_count= EmployeeRegister.objects.filter(empstate='').count()

        reg_ojt= Register.objects.filter(reg_state=None)
        reg_ojt_count= Register.objects.filter(reg_state=None).count()

        inex= IncomeExpence.objects.filter(exin_state=None)
        inex_count= IncomeExpence.objects.filter(exin_state=None).count()

        fxex= FixedExpence.objects.filter(fixed_state=None)
        fxex_count= FixedExpence.objects.filter(fixed_state=None).count()

        holid= Company_Holidays.objects.filter(ch_state=None)
        holid_count= Company_Holidays.objects.filter(ch_state=None).count()

        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       

        content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'reg_emp':reg_emp,
                    'reg_emp_count':reg_emp_count,
                    'reg_ojt':reg_ojt,
                    'reg_ojt_count':reg_ojt_count,
                    'inex':inex,
                    'inex_count':inex_count,
                    'fxex':fxex,'fxex_count':fxex_count,
                    'holid':holid,'holid_count':holid_count
                   }
        
        content = {**content, **common_accdash_data}

        return render(request,'account/emplyee_allocate_list.html',content)

    else:
        return redirect('/')
    

#======================= ALL Payment Section ====================================

def pyment_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        ojt_reg=Register.objects.filter(reg_status=1,payment_status=0,reg_state=acc_state)
        ojt_count=Register.objects.filter(reg_status=1,payment_status=0,reg_state=acc_state).count()
        pay_history = PaymentHistory.objects.filter(reg_id__in=ojt_reg,admin_payconfirm=0)


        # Payment save---------------
        if request.method =='POST':
 
            reg=Register.objects.get(id=int(request.POST['payname']))

            pay_amt=int(request.POST['payamount'])
            next_date=request.POST['pay_nextdate']
            
            paymt=PaymentHistory()
            paymt.reg_id=reg
            paymt.head_name=request.POST['payhead']
            paymt.payintial_amt=pay_amt
            paymt.paydofj=request.POST['paydate']
            paymt.paybalance_amt=int(reg.regbalance_amt) - pay_amt
            paymt.paytotal_amt=int(reg.reg_payedtotal)
            paymt.pay_state=acc_state
            paymt.save()

           

            if next_date:
                reg.next_pay_date=request.POST['pay_nextdate']

            else:
                # Calculate the date after 30 days
            
                current_date = reg.next_pay_date

                if pay_amt >= int(reg.fixed_intial_amt):
                
                    after_days = current_date + timedelta(days=30)
                else:
                    after_days = current_date + timedelta(days=15)

                reg.next_pay_date=after_days
           
            reg.save()
            success_msg='Success! Payments Details add successful.'

            content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'ojt_reg':ojt_reg,
                    'ojt_count':ojt_count,
                    'success_msg':success_msg,
                    'pay_history':pay_history
                   }
            
        #-------------------------------------------------------------
        else:
            content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'ojt_reg':ojt_reg,
                    'ojt_count':ojt_count,
                    'pay_history':pay_history
                   }

        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       

        
        content = {**content, **common_accdash_data}

        return render(request,'account/payment_add_page.html',content)

    
    else:
        return redirect('/')


# Featching the trainee to add payments----------
def addpayment_details(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        try:
            reg_dt=Register.objects.get(id=pk)

        except Register.DoesNotExist:

            reg_dt=None

        ojt_reg=Register.objects.filter(reg_status=1,payment_status=0,reg_state=acc_state)
        ojt_count=Register.objects.filter(reg_status=1,payment_status=0,reg_state=acc_state).count()
        pay_history = PaymentHistory.objects.filter(reg_id__in=ojt_reg,admin_payconfirm=0)

        # Payment Edit---------------
        if request.method =='POST':
 
            
            pay_amt=int(request.POST['payamount'])
            next_date=request.POST['pay_nextdate']
            
            paymt=PaymentHistory.objects.get(id=int(request.POST['editpayname']))
          
            reg_dt=Register.objects.get(id=paymt.reg_id.id)

            paymt.head_name=request.POST['payhead']
            paymt.payintial_amt=pay_amt
            paymt.paydofj=request.POST['paydate']
            paymt.paybalance_amt=int(reg_dt.regbalance_amt) - pay_amt
            paymt.paytotal_amt=int(reg_dt.reg_payedtotal)
            paymt.pay_state =acc_state
            paymt.save()

           

            if next_date:
                reg_dt.next_pay_date=request.POST['pay_nextdate']

            else:
                # Calculate the date after 30 days
            
                current_date = reg_dt.next_pay_date

                if pay_amt >= int(reg_dt.fixed_intial_amt):
                
                    after_days = current_date + timedelta(days=30)
                else:
                    after_days = current_date + timedelta(days=15)

                reg_dt.next_pay_date=after_days
           
            reg_dt.save()
            success_msg='Success! Payments edit  successful.'

            content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'ojt_reg':ojt_reg,
                    'ojt_count':ojt_count,
                    'success_msg':success_msg,
                    'reg_dt':reg_dt,
                    'pay_history':pay_history
                   }
            
        #-------------------------------------------------------------
        else:
            content={'account_DHB':account_DHB,
                    'acc_state':acc_state,
                    'ojt_reg':ojt_reg,
                    'ojt_count':ojt_count,
                    'reg_dt':reg_dt,
                    'pay_history':pay_history
                   }

        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas       

        content = {**content, **common_accdash_data}

        return render(request,'account/payment_add_page.html',content)
    

    else:
            return redirect('/')



def ojt_payment_list_single(request):
   
    reg= Register.objects.get(id=int(request.GET.get('regid')))
    pay_list=PaymentHistory.objects.filter(reg_id=reg).order_by('-id')
    pay_list_count=PaymentHistory.objects.filter(reg_id=reg).count()


    content = {'pay_list':pay_list,
               'pay_list_count':pay_list_count,
               'reg':reg}
    return render(request,'account/ojt_payment_list_single.html',content)


def ojt_payment_edit(request):

    pay_id=int(request.GET.get('payid'))
    pay_his=PaymentHistory.objects.get(id=pay_id)
    content = {
       'name': pay_his.reg_id.fullName,
       'head_name': pay_his.head_name,
       'amount': pay_his.payintial_amt,
       'paydate': pay_his.paydofj,
       'nextdate': pay_his.reg_id.next_pay_date,
       'edit_id':pay_id,

    }
    return JsonResponse(content)


#====================================================================================



def track_payments(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #---------------------------------------------------------------

        
    
        up_payments = upcoming_state_payments(request,acc_state)  

        content={'account_DHB':account_DHB,
                        'acc_state':acc_state,
                        
                    }
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas    

        content = {**content, **common_accdash_data, **up_payments}

        return render(request,'account/track_Payments.html',content) 

    
    else:
        return redirect('/')



def quick_search(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')

        if pk == 0:
            
            cur_date=datetime.now().date()
            fr_date=datetime(cur_date.year, cur_date.month, 1).date()
            to_date = fr_date + timedelta(days=6)
        
            reg=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,payment_status=0)
            reg_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,payment_status=0).count()
            tk_amount=0
            for i in reg:
                tk_amount=tk_amount + int(i.next_pat_amt)

            content={'fr_date':fr_date,
                    'to_date':to_date,
                    'reg_count':reg_count,
                    'tk_amount':tk_amount,
                    'cur_date':cur_date
                    }
            return render(request,'account/track_Payments.html',{'reg':reg,'content':content})
        

        elif pk == 1:

            cur_date=datetime.now().date()
            fr_date=datetime(cur_date.year, cur_date.month, 8).date()
            to_date = fr_date + timedelta(days=7)

            reg=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,payment_status=0)
            reg_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,payment_status=0).count()
            tk_amount=0
            for i in reg:
                tk_amount=tk_amount + int(i.next_pat_amt)

            content={'fr_date':fr_date,
                    'to_date':to_date,
                    'reg_count':reg_count,
                    'tk_amount':tk_amount,
                    'cur_date':cur_date
                    }
            return render(request,'account/track_Payments.html',{'reg':reg,'content':content})
        
        elif pk == 2:

            cur_date=datetime.now().date()
            fr_date=datetime(cur_date.year, cur_date.month, 16).date()
            last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
            to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        
            reg=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,payment_status=0)
            reg_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,payment_status=0).count()
            tk_amount=0
            for i in reg:
                tk_amount=tk_amount + int(i.next_pat_amt)

            content={'fr_date':fr_date,
                    'to_date':to_date,
                    'reg_count':reg_count,
                    'tk_amount':tk_amount,
                    'cur_date':cur_date
                    }
            return render(request,'account/track_Payments.html',{'reg':reg,'content':content})

        else:
            return redirect('track_payments')
        
    else:
        return redirect('/')



def upcoming_payments_list(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        if request.method =='POST':
            fr_date=request.POST['up_fr_data']
            to_date=request.POST['up_to_date']
            cur_date=datetime.now().date()
            reg=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,payment_status=0)
            reg_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,payment_status=0).count()
            tk_amount=0
            for i in reg:
                tk_amount=tk_amount + int(i.next_pat_amt)

            content={'fr_date':fr_date,
                    'to_date':to_date,
                    'reg_count':reg_count,
                    'tk_amount':tk_amount,
                    'cur_date':cur_date
                    }
            return render(request,'account/track_Payments.html',{'reg':reg,'content':content})
        else:
            return redirect('track_payments')
        
    else:
        return redirect('/')


def allpayments(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        reg=Register.objects.all()
        cur_date=datetime.now().date()
        return render(request,'account/allpaymets.html',{'reg':reg,'cur_date':cur_date})
     
    else:
        return redirect('/')


def pending_payments(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        reg=Register.objects.filter(payment_status=0)
        cur_date=datetime.now().date()
        return render(request,'account/allpaymets.html',{'reg':reg,'cur_date':cur_date})
    else:
            return redirect('/')
    

def completed_payments(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        reg=Register.objects.filter(payment_status=1)
        cur_date=datetime.now().date()
        return render(request,'account/allpaymets.html',{'reg':reg,'cur_date':cur_date})
    else:
            return redirect('/')
    

def incompleted_payments(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        reg=Register.objects.filter(payment_status=2)
        cur_date=datetime.now().date()
        return render(request,'account/allpaymets.html',{'reg':reg,'cur_date':cur_date})
    
    else:
            return redirect('/')


def paysearch(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        if request.method =='POST':
            
            payhis=PaymentHistory.objects.filter(paydofj__gte=request.POST['pfr_data'],paydofj__lte=request.POST['pto_date']).values_list('reg_id').distinct()
            cur_date=datetime.now().date()
        
            reg=Register.objects.filter(id__in=payhis)
            return render(request,'account/allpaymets.html',{'reg':reg,'cur_date':cur_date})
        else:
            return redirect('allpayments')
    else:
        return redirect('/')
    


def Users_list(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')

        dept=Department.objects.all()

        try:
            reg=Register.objects.all()
            editreg=Register.objects.all().first()
            if editreg:
                return render(request,'account/users.html',{'editreg':editreg,'reg':reg,'dept':dept})
            else:
                return redirect('dashboard')

        except Register.DoesNotExist:
            editreg=None
            return redirect('dashboard')
        
    else:
        return redirect('/')

    
def edit_user(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        reg=Register.objects.all()
        dept=Department.objects.all()
        editreg=Register.objects.get(id=pk)
        return render(request,'account/users.html',{'editreg':editreg,'reg':reg,'dept':dept})
    else:
        return redirect('/')



def payment_details(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        pay_dt=PaymentHistory.objects.filter(reg_id_id=pk)
        reg=Register.objects.filter(reg_status=1)
        return render(request,'account/Payment_form.html',{'reg':reg,'pay_dt':pay_dt})
    
    else:
        return redirect('/')
    
    




def register_Details(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        dept=Department.objects.all()

        if request.method =='POST':
            reg=Register()
            reg.fullName=request.POST['name']
            reg.Phone=request.POST['phno']
            reg.dofj=request.POST['dfj']
            reg.refrence=request.POST['refby']
            intial_amt=int(request.POST['init_amunt'])
            total_amt=int(request.POST['tot_amount'])
            reg.fixed_intial_amt= int(request.POST['fixedinit_amunt'])
            cal=int(request.POST['fixedinit_amunt'])
          
            #reg.next_pat_amt=cal 
            reg.regtotal_amt=total_amt
            reg.dept_id=Department.objects.get(id=request.POST['dept'])
            next_date=request.POST['nxtpdof']

            if next_date:
                reg.next_pay_date=request.POST['nxtpdof']

            else:
               
                current_date = request.POST['dfj']
                current_date = datetime.strptime(current_date, "%Y-%m-%d").date()
                # Calculate the date after 30 days
                if intial_amt >= cal:
                    after_days = current_date + timedelta(days=30)
                   
                # Calculate the date after 15 days
                else:
                     after_days = current_date + timedelta(days=15)
                   
                reg.next_pay_date=after_days

            reg.save()

            payhis=PaymentHistory()
            payhis.head_name='Initial Payment'
            payhis.paydofj=(request.POST['dfpayment'])
            payhis.payintial_amt=intial_amt
            payhis.paytotal_amt=total_amt
            

            payhis.pay_status=1
            payhis.reg_id=reg
            payhis.save()

            reg.firstpay_id=payhis.id
            reg.save()

            # Send an email
            # subject = 'Payment Confirmation'
            # message = 'Here is the message.'
            # email_from = 'shebinshaji99@gmail.com'
            # recipient_list = ['shebinshaji81@gmail.com',]
            # send_mail(subject, message, email_from, recipient_list, fail_silently=False)

            msg=1
            reg=Register.objects.filter(reg_status=0)
            payhis=PaymentHistory.objects.all()
            return render(request,'account/Register_form.html',{'msg':msg,'dept':dept,'reg':reg,'payhis':payhis})
        else:
            return redirect('Register_form')
    else:
        return redirect('/')

def edit_Details(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        if request.method =='POST':
            reg=Register.objects.get(id=pk)
            reg.fullName=request.POST['editname']
            reg.Phone=request.POST['editphno']

            if request.POST['editdfj']:
                reg.dofj=request.POST['editdfj']
            else:
                reg.dofj= reg.dofj
            
            if request.POST['editnxtpdof']:
                reg.next_pay_date= request.POST['editnxtpdof']
            else:
                reg.next_pay_date= reg.next_pay_date
            
            reg.refrence=request.POST['editrefby']
            reg.dept_id=Department.objects.get(id=request.POST['editdept'])
            reg.save()
            msge='Data Updated'
            reg=Register.objects.all()
            dept=Department.objects.all()
            editreg=Register.objects.all().first()
            return render(request,'account/users.html',{'editreg':editreg,'reg':reg,'dept':dept,'msge':msge})

        else:
            return redirect('Users_list')
    else:
        return redirect('/')




    

# def confirm(request,pk):
#     reg1=Register.objects.get(id=pk, reg_status=0)
#     reg1.reg_status=1
   
#     dept=Department.objects.filter(dpt_Status=1)
#     reg=Register.objects.filter(reg_status=0)
#     payhis=PaymentHistory.objects.get(reg_id_id=reg1.id)
#     reg1.regbalance_amt=int(reg1.regtotal_amt) - int(payhis.payintial_amt)
#     reg1.save()

#     payhis.pay_status=1
#     payhis.paybalance_amt=int(reg1.regbalance_amt)
#     payhis.save()

#     payhis=PaymentHistory.objects.all()
#     msg=2
#     return render(request,'account/Register_form.html',{'msg':msg,'dept':dept,'reg':reg,'payhis':payhis})



def paymentfull_view(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        payhis=PaymentHistory.objects.all()
        return render(request,'account/paymentsfull_View.html',{'payhis':payhis})
    
    else:
        return redirect('/')





# Account Section-------------- 

def accounts(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        in_ex_count=IncomeExpence.objects.filter(exin_date__gte=fr_date,exin_date__lte=to_date).count()
        fixed_ex_count=FixedExpence.objects.all().count()
        

        income=IncomeExpence.objects.filter(exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        expence=IncomeExpence.objects.filter(exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        if not income:
            income=1
        if not expence:
            expence=1
        balans=int(income) -int(expence)
        
        bal_p= income - expence 
        if bal_p < 0:
            
            bal_p=-(bal_p)
        
        exp_pr=int(expence) / int(bal_p + income + expence)
        inc_pr=int(income) / int(bal_p + income + expence)
        bal_pr=int(bal_p) / int(bal_p + income + expence)
        
        

       
        emp_reg_count=EmployeeRegister.objects.filter(emp_status=1).count()
        emp_salary_count=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empdofj__lt=fr_date).count()
        content={'emp_reg_count':emp_reg_count,
                 'emp_salary_count':emp_salary_count,
                 'income':income,
                 'expence':expence,
                 'balans':balans,
                 'bal_pr':bal_pr,
                 'exp_pr':exp_pr,
                 'in_ex_count':in_ex_count,
                 'fixed_ex_count':fixed_ex_count,'inc_pr':inc_pr
                 
                 }
        
        return render(request,'account/accounts.html',{'content':content})
    else:
        return redirect('/')
    


# Income Expence ----------------------
def income_expence_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        exp_income=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date')
        exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date').count()

        exp_income_sum=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        exp_expence_sum=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']

        if request.method =='POST':

           
            if request.POST['exincom']:
                ex_in=IncomeExpence.objects.get(id=int(request.POST['exincom']))
                ex_in.exin_head_name=request.POST['exin_head_name'].upper()

                if request.POST['exin_date']:
                    ex_in.exin_date=request.POST['exin_date']
                else:
                    request.POST['exin_date']=request.POST['exin_date']

                ex_in.exin_amount=request.POST['exin_amt']
                ex_in.exin_dese=request.POST['exin_dese']
                ex_in.exin_typ=request.POST['exin_type']
                ex_in.exin_status=1
                ex_in.exin_state=acc_state
                ex_in.save()
                success_msg='Success! One Record edit successfully.'
                exp_income=IncomeExpence.objects.filter(exin_status=1).order_by('exin_date')
            
            else:

                ex_in=IncomeExpence()
                ex_in.exin_head_name=request.POST['exin_head_name'].upper()
                ex_in.exin_date=request.POST['exin_date']
                ex_in.exin_amount=request.POST['exin_amt']
                ex_in.exin_dese=request.POST['exin_dese']
                ex_in.exin_typ=request.POST['exin_type']
                ex_in.exin_status=1
                ex_in.exin_state=acc_state
                ex_in.save()
                success_msg='Success! One Record add successfully.'
            
            exp_income=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date')
            exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date').count()

            exp_income_sum=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
            exp_expence_sum=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']

            content={'account_DHB':account_DHB,
                                'exp_income':exp_income,
                                'exp_income_count':exp_income_count,
                                'success_msg':success_msg,
                                'exp_income_sum':exp_income_sum,
                                'exp_expence_sum':exp_expence_sum,
                                'acc_state':acc_state}
        else:
             content={'account_DHB':account_DHB,
                                'exp_income':exp_income,
                                'exp_income_count':exp_income_count,
                                'exp_income_sum':exp_income_sum,
                                'exp_expence_sum':exp_expence_sum,
                                'acc_state':acc_state}

            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/income_expence.html',content)
       
    else:
        return redirect('/')
    
    
def income_expence_edit(request,inex_edit):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 


        exp_income=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date')
        exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date').count()

        exp_income_sum=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        exp_expence_sum=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']

        exp_income_edit=IncomeExpence.objects.get(id=inex_edit)

        content={'account_DHB':account_DHB,
                            'exp_income':exp_income,
                            'exp_income_count':exp_income_count,
                            'exp_income_edit':exp_income_edit,
                            'exp_income_sum':exp_income_sum,
                            'exp_expence_sum':exp_expence_sum,
                            'acc_state':acc_state}

            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/income_expence.html',content)

    else:
        return redirect('/')
    


def income_expence_delete(request,incom_delete):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
        
        # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
       
        ex_in=IncomeExpence.objects.get(id=incom_delete)  
        ex_in.delete()
        error_msg='Opps! Record removed.'
        exp_income=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date')
        exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date').count()

        exp_income_sum=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        exp_expence_sum=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']

        content={'account_DHB':account_DHB,
                            'exp_income':exp_income,
                            'exp_income_count':exp_income_count,
                            'error_msg':error_msg,
                            'exp_income_sum':exp_income_sum,
                            'exp_expence_sum':exp_expence_sum,
                            'acc_state':acc_state}

            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/income_expence.html',content)

    else:
        return redirect('/')

def income_expence_search(request):
     if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        exp_income=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date')
        exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_state=acc_state,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('exin_date').count()

        if request.method =='POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']

            if sdate and edate:
        

                exp_income=IncomeExpence.objects.filter(exin_date__gte=sdate,exin_date__lte=edate,exin_status=1,exin_state=acc_state).order_by('exin_date')

                exp_income_sum=IncomeExpence.objects.filter(exin_date__gte=sdate,exin_date__lte=edate,exin_status=1,exin_state=acc_state,exin_typ=1).aggregate(Sum('exin_amount'))['exin_amount__sum']
                exp_expence_sum=IncomeExpence.objects.filter(exin_date__gte=sdate,exin_date__lte=edate,exin_status=1,exin_state=acc_state,exin_typ=2).aggregate(Sum('exin_amount'))['exin_amount__sum']
                
                exp_income_count=IncomeExpence.objects.filter(exin_date__gte=sdate,exin_date__lte=edate,exin_status=1,exin_state=acc_state).order_by('exin_date').count()

                content={'account_DHB':account_DHB,
                                    'exp_income':exp_income,
                                    'exp_income_count':exp_income_count,
                                    'exp_income_sum':exp_income_sum,
                                    'exp_expence_sum':exp_expence_sum,
                                    'acc_state':acc_state}
                common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
                content = {**content, **common_accdash_data}
                return render(request,'account/income_expence.html',content)
            else:
                return redirect('income_expence_form')



# Fixed Expence------------------
def fixed_expence(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        fixedexp=FixedExpence.objects.filter(fixed_state=acc_state)
        fixedexp_count=FixedExpence.objects.filter(fixed_state=acc_state).count()

        if request.method =='POST':

            if request.POST['fixed_id']:

                fixededit=FixedExpence.objects.get(fixed_status=1,id=int(request.POST['fixed_id']))
                fixededit.fixed_head_name=request.POST['fixed_head_name'].upper()
               
                fixededit.fixed_amount=request.POST['fixed_amt']
                fixededit.fixed_dese=request.POST['fixed_dese']
                fixededit.fixed_status=1
                fixededit.fixed_state=acc_state
             
                if request.POST['fixed_date']:
                    fixededit.fixed_date=request.POST['fixed_date']
                else:
                    fixededit.fixed_date=fixedexp_reg.fixed_date

                fixededit.save()
                success_msg='Success ! Fixed expence edit successfuly.'

                fixedexp=FixedExpence.objects.filter(fixed_state=acc_state)
                fixedexp_count=FixedExpence.objects.filter(fixed_state=acc_state).count()
        

            else:
    
                fixedexp_reg=FixedExpence()
                fixedexp_reg.fixed_head_name=request.POST['fixed_head_name'].upper()
                fixedexp_reg.fixed_date=request.POST['fixed_date']
                fixedexp_reg.fixed_amount=request.POST['fixed_amt']
                fixedexp_reg.fixed_dese=request.POST['fixed_dese']
                fixedexp_reg.fixed_status=1
                fixedexp_reg.fixed_state=acc_state
                fixedexp_reg.save()
                success_msg='Success ! Fixed expence add successfuly.'

                fixedexp=FixedExpence.objects.filter(fixed_state=acc_state)
                fixedexp_count=FixedExpence.objects.filter(fixed_state=acc_state).count()

            content={'account_DHB':account_DHB,
                            'fixedexp':fixedexp,
                            'fixedexp_count':fixedexp_count,
                            'success_msg':success_msg,
                            'acc_state':acc_state}
        else:

            content={'account_DHB':account_DHB,
                            'fixedexp':fixedexp,
                            'fixedexp_count':fixedexp_count,
                            'acc_state':acc_state}

            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/fixed_expence.html',content)
       
       
    else:
        return redirect('/')


def fixed_edit(request,pk):
    
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        fixedexp=FixedExpence.objects.filter(fixed_state=acc_state)
        fixedexp_count=FixedExpence.objects.filter(fixed_state=acc_state).count()

        fixededit=FixedExpence.objects.get(id=pk)
        content={'account_DHB':account_DHB,
                        'fixedexp':fixedexp,
                        'fixedexp_count':fixedexp_count,
                        'fixededit':fixededit,
                        'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/fixed_expence.html',content)
       
       
    else:
        return redirect('/')
    

def fixed_delete(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        fixededit=FixedExpence.objects.get(fixed_status=1,id=pk)
        fixededit.delete()
        error_msg='Opps! Fixed Expence removed.'
       
      
        fixedexp=FixedExpence.objects.filter(fixed_state=acc_state)
        fixedexp_count=FixedExpence.objects.filter(fixed_state=acc_state).count()

      
        content={'account_DHB':account_DHB,
                        'fixedexp':fixedexp,
                        'fixedexp_count':fixedexp_count,
                        'error_msg':error_msg,
                        'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/fixed_expence.html',content)
        
    else:
        return redirect('/')
    
   
def fixed_change_status(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
        fixededit=FixedExpence.objects.get(id=pk)
        if fixededit.fixed_status == 1:
            fixededit.fixed_status=0
            success_msg= 'Deactivated fixed expence'
        else:
             fixededit.fixed_status=1
             success_msg= 'Activated fixed expence'
        fixededit.save()

        fixedexp=FixedExpence.objects.filter(fixed_state=acc_state)
        fixedexp_count=FixedExpence.objects.filter(fixed_state=acc_state).count()

      
        content={'account_DHB':account_DHB,
                        'fixedexp':fixedexp,
                        'fixedexp_count':fixedexp_count,
                        'success_msg':success_msg,
                        'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/fixed_expence.html',content)
        
    else:
        return redirect('/')
    

# state Holiday -------------------
def company_holoidays(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        comp_holidays=Company_Holidays.objects.filter(ch_state=acc_state).order_by('-ch_sdate')
        comp_holidays_count=Company_Holidays.objects.filter(ch_state=acc_state).count()

        if request.method == 'POST':
            
            
            if request.POST.get('cmphid'):
                comp_holidays_edit=Company_Holidays.objects.get(id=int(request.POST['cmphid']))
                comp_holidays_edit.ch_sdate=request.POST['cmphsdate']
                comp_holidays_edit.ch_edate=request.POST['cmphedate']
                comp_holidays_edit.ch_no=request.POST['cmphno']
                comp_holidays_edit.ch_state=acc_state

                e = datetime.strptime(request.POST['cmphedate'], '%Y-%m-%d')
                s = datetime.strptime(request.POST['cmphsdate'], '%Y-%m-%d')

                month_days = (e - s).days + 1
                comp_holidays_edit.ch_workno=int(month_days) - int(request.POST['cmphno'])
               
                comp_holidays_edit.save()
                success_msg="Success! State Holiday edit Successfuly."

                comp_holidays=Company_Holidays.objects.filter(ch_state=acc_state).order_by('-ch_sdate')
                comp_holidays_count=Company_Holidays.objects.filter(ch_state=acc_state).count()

                content={'account_DHB':account_DHB,
                    
                        'comp_holidays':comp_holidays,
                        'comp_holidays_count':comp_holidays_count,
                        'success_msg':success_msg,
                        'acc_state':acc_state}
                
            else:
                comp_holiday=Company_Holidays()
                comp_holiday.ch_sdate=request.POST['cmphsdate']
                comp_holiday.ch_edate=request.POST['cmphedate']
                comp_holiday.ch_no=request.POST['cmphno']
                comp_holiday.ch_state=acc_state


                #company workdays Calculations
                e = datetime.strptime(request.POST['cmphedate'], '%Y-%m-%d')
                s = datetime.strptime(request.POST['cmphsdate'], '%Y-%m-%d')

                month_days = (e - s).days + 1
                comp_holiday.ch_workno=int(month_days) - int(request.POST['cmphno'])
                
                comp_holiday.save()
                success_msg="Success! State Holiday Add Successfuly."

                comp_holidays=Company_Holidays.objects.filter(ch_state=acc_state).order_by('-ch_sdate')
                comp_holidays_count=Company_Holidays.objects.filter(ch_state=acc_state).count()

                content={'account_DHB':account_DHB,
                        
                            'comp_holidays':comp_holidays,
                            'comp_holidays_count':comp_holidays_count,
                            'success_msg':success_msg,
                            'acc_state':acc_state}

  
        else:

            content={'account_DHB':account_DHB,
                        'comp_holidays':comp_holidays,
                        'comp_holidays_count':comp_holidays_count,
                        'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/company_holidays.html',content)
    else:
        return redirect('/')
    

def company_holidy_edit(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
        comp_holidays=Company_Holidays.objects.filter(ch_state=acc_state).order_by('-ch_sdate')
        comp_holidays_count=Company_Holidays.objects.filter(ch_state=acc_state).count()

        

        comp_holidays_edit=Company_Holidays.objects.get(id=pk)

        content={'account_DHB':account_DHB,
                        'comp_holidays':comp_holidays,
                        'comp_holidays_count':comp_holidays_count,
                        'comp_holidays_edit':comp_holidays_edit,
                        'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/company_holidays.html',content)
       
    else:
        return redirect('/')



def recipt_data(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        r_data=Receipt_Data.objects.all().first()
        
        cur_date=datetime.now().date()

        return render(request,'account/recept_data.html',{'r_data':r_data,'cur_date':cur_date})
        
    else:
        return redirect('/')
    

def recipt_data_save(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.method =='POST':

            check=Receipt_Data.objects.all()
            if check:
                r_data=Receipt_Data.objects.first()
                r_data.auth_fullname=request.POST['aut_name']

                if request.FILES.get('aut_signature'):
                    r_data.auth_signature=request.FILES.get('aut_signature')
                else:
                      r_data.auth_signature =  r_data.auth_signature
                r_data.company_name=request.POST['company']
                r_data.company_address1=request.POST['company_add1']
                r_data.company_address2=request.POST['company_add2']
                r_data.company_address3=request.POST['company_add3']

                if request.FILES.get('company_logo'):
                    r_data.company_logo=request.FILES.get('company_logo')
                else:
                    r_data.company_logo= r_data.company_logo

                if request.FILES.get('company_seal'):
                    r_data.company_seal=request.FILES.get('company_seal')
                else:
                    r_data.company_seal= r_data.company_seal
                r_data.company_email=request.POST['company_email']
                r_data.company_site=request.POST['company_site']
                r_data.save()

            else:
                r_data=Receipt_Data()
                r_data.auth_fullname=request.POST['aut_name']
                r_data.auth_signature=request.FILES.get('aut_signature')
                r_data.company_name=request.POST['company']
                r_data.company_address1=request.POST['company_add1']
                r_data.company_address2=request.POST['company_add2']
                r_data.company_address3=request.POST['company_add3']
                r_data.company_logo=request.FILES.get('company_logo')
                r_data.company_seal=request.FILES.get('company_seal')
                r_data.company_email=request.POST['company_email']
                r_data.company_site=request.POST['company_site']
                r_data.save()
                r_data=Receipt_Data.objects.all().first()
            
            cur_date=datetime.now().date()
        return render(request,'account/recept_data.html',{'r_data':r_data,'cur_date':cur_date})
        
    else:
        return redirect('/')



 
def salary_expence(request):
    
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        emp_salary_tol=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empdofj__lt=fr_date).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']

        salary=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        content={'emp_salary_tol':emp_salary_tol,
                 'to_date':to_date,
                 'fr_date':fr_date,
                 'cur_date':cur_date,
                 'salary_tol':salary_tol,
                 }
        
        return render(request,'account/salary_expence.html',{'content':content,'salary':salary,})
    else:
        return redirect('/')
    

def salary_expence_form(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        
        
        current_year = datetime.now().year

       
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        emp_salary_all=EmployeeSalary.objects.filter(emp_paidstatus=1)

        emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,empstate=acc_state.state_name).exclude(id__in=emp_salary.values_list('empreg_id', flat=True))
        emp_reg_count=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,empstate=acc_state.state_name).exclude(id__in=emp_salary.values_list('empreg_id', flat=True)).count()


        content={'account_DHB':account_DHB,
                    'months':months,'years':years,
                    'emp_reg':emp_reg,
                    'emp_salary':emp_salary,
                    'emp_salary_all':emp_salary_all,
                    'current_year':current_year,
                    'emp_reg_count':emp_reg_count,
                    'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/salary_expence_form.html',content)
       
    else:
        return redirect('/')
    

#Employee pending salary -------------------------

def employee_pending_salary(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
       
        
        if request.method =='POST': 
            months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
            years = [(str(i), str(i)) for i in range(2021, 2031)]
        

            current_year = datetime.now().year
            content={'months':months,'years':years}
            # Here calculating the working days of selected month
            m = date(2000, int(request.POST['empsalary_month']), 1).strftime('%B')
            startdate = date(int(request.POST['empsalary_year']), int(request.POST['empsalary_month']), 1)
            my= m + ' ' + request.POST['empsalary_year']
            
            emp_sal=EmployeeSalary.objects.filter(empsalary_month=my)
            emp_reg=EmployeeRegister.objects.filter(empdofj__lt=startdate,emp_status=1,empstate=acc_state.state_name).exclude(id__in=emp_sal.values_list('empreg_id', flat=True))
            emp_reg_count=EmployeeRegister.objects.filter(empdofj__lt=startdate,emp_status=1,empstate=acc_state.state_name).exclude(id__in=emp_sal.values_list('empreg_id', flat=True)).count()
            
            content={'account_DHB':account_DHB,
                    'months':months,'years':years,
                    'emp_reg':emp_reg,
                    'current_year':current_year,
                    'emp_reg_count':emp_reg_count,
                    'acc_state':acc_state,'month_name':m}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/salary_expence_form.html',content)

    else:
            return redirect('/')


# Adding Employee details to pay form ----------------------
    
def salary_expence_add(request,pk):
     
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        
        
        current_year = datetime.now().year

        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)

       
        try:
            emp_reg_edit=EmployeeRegister.objects.get(emp_status=1,id=pk,emp_salary_status=1)

            emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
            emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,empstate=acc_state.state_name).exclude(id__in=emp_salary.values_list('empreg_id', flat=True))
            emp_reg_count=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,empstate=acc_state.state_name).exclude(id__in=emp_salary.values_list('empreg_id', flat=True)).count()

            content={'account_DHB':account_DHB,
                    'months':months,'years':years,
                    'emp_reg':emp_reg,
                    'emp_salary':emp_salary,
                    'emp_reg_edit':emp_reg_edit,
                    'current_year':current_year,
                    'emp_reg_count':emp_reg_count,
                    'acc_state':acc_state}
            

        except  EmployeeRegister.DoesNotExist:
            error_msg='Opps! Employee salary account not active'

    
            emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
            emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,empstate=acc_state.state_name).exclude(id__in=emp_salary.values_list('empreg_id', flat=True))
            emp_reg_count=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,empstate=acc_state.state_name).exclude(id__in=emp_salary.values_list('empreg_id', flat=True)).count()

            content={'account_DHB':account_DHB,
                        'months':months,'years':years,
                        'emp_reg':emp_reg,
                        'emp_salary':emp_salary,
                        'current_year':current_year,
                        'emp_reg_count':emp_reg_count,
                        'error_msg':error_msg,
                        'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/salary_expence_form.html',content)
        
    else:
        return redirect('/')
    

def employee_salary_save(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
    
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]

        current_year = datetime.now().year

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        
        
        if request.method =='POST':

            if request.POST['Emp_regid'] == '':

               return redirect('salary_expence_form')
            
            emp_reg=EmployeeRegister.objects.get(id=request.POST['Emp_regid']) # Get the employee details

            # Here calculating the working days of selected month

            mon =int(request.POST['empsalary_month'])
            ye = int(request.POST['empsalary_year'])
           
            startdate = date(ye, mon, 1)
            last_day_of_month = startdate.replace(day=28) + timedelta(days=4)
            enddate = last_day_of_month - timedelta(days=last_day_of_month.day)
            month_days = (enddate - startdate).days + 1


            # Salary Calculations  
            
           

            try:

                comp_holiday=Company_Holidays.objects.get(ch_sdate__gte=startdate,ch_edate__lte=enddate,ch_state=acc_state.id)
                work_days=int(month_days) - int(comp_holiday.ch_no) 
                leavefull=int(request.POST['leave_full'])
                leavehalf=int(request.POST['leave_half'])
                w_delay=int(request.POST['work_delay'])
                any_other=int(request.POST['other_amt'])
                any_dother=int(request.POST['other_damt'])

                if not request.POST['leave_full']:
                    leavefull=0
                if not request.POST['leave_half']:
                    leavehalf=0
                if not request.POST['work_delay']:
                    w_delay=0
                if not request.POST['other_amt']:
                    any_other=0
                if not request.POST['other_damt']:
                    any_dother=0

                conf_salary=emp_reg.empconfirmsalary
                one_day_salary=int(conf_salary / work_days)

                full_day_leave_amt=int(one_day_salary) * int(leavefull)
                half_day_leave_amt=int(one_day_salary / 2) * int(leavehalf)
                w_delay_amt=int(one_day_salary) * int(w_delay)
                net_salary=int(conf_salary) - int(full_day_leave_amt + half_day_leave_amt + w_delay_amt)
                net_salary=int(net_salary) + int(any_other)
                net_salary=int(net_salary) - int(any_dother)

                m = date(2000, int(request.POST['empsalary_month']), 1).strftime('%B')
                my = m + ' ' + request.POST['empsalary_year']

                if EmployeeSalary.objects.filter(empreg_id=emp_reg,empsalary_month=my).exists():
                    
                    print('Salary Already Payed')
                    success_msg='Success! Salary Already Payed.'
                
                else:

            
                    emp_reg.emptol_salary= int(emp_reg.emptol_salary) + int(net_salary)
                    emp_reg.emp_salary_status=1
                    emp_reg.save()

                    emp_salary=EmployeeSalary()
                    emp_salary.empreg_id=emp_reg
                
                    m = date(2000, int(request.POST['empsalary_month']), 1).strftime('%B')
                    
                    emp_salary.empsalary_month= m + ' ' + request.POST['empsalary_year']
                    
                    if request.POST['empsalary_date']:
                        emp_salary.empslaray_date=request.POST['empsalary_date']
                    else:
                        emp_salary.empslaray_date=cur_date

                    emp_salary.emppaid_amt= int(net_salary)
                    emp_salary.empfull_leave=leavefull
                    emp_salary.emphalf_leave=leavehalf
                    emp_salary.empfull_leave_amt=full_day_leave_amt
                    emp_salary.emphalf_leave_amt=half_day_leave_amt
                    emp_salary.emp_delay=w_delay
                    emp_salary.emp_delay_amt=w_delay_amt
                    emp_salary.emp_other_amt=any_other
                    emp_salary.emp_other_damt=any_dother
                    emp_salary.emp_paidstatus=1
                    emp_salary.save()
                    success_msg='Sucees! Salary Payment add successfuly.'

                    # Salay Expence adding to IncomeExpence Table
                    if EmployeeSalary.objects.exists():
                        
                        if request.POST['empsalary_date']:

                            pay_date = datetime.strptime(request.POST['empsalary_date'], '%Y-%m-%d').date()
                        else:
                           pay_date= cur_date

                       
                        # Calculate start and end datetime objects for the month corresponding to input_date
                        payfr_date = pay_date.replace(day=1)

                        last_daymonth = payfr_date.replace(day=28) + timedelta(days=4)
                        payto_date = last_daymonth - timedelta(days=last_daymonth.day)

                        
                    
                        try:
                            inexp=IncomeExpence.objects.filter(exin_head_name='SALARY',exin_date__gte=payfr_date,exin_date__lte=payto_date,exin_state=acc_state).first()
                            emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date,empstate=acc_state.state_name)
                            sal_exp=EmployeeSalary.objects.filter(empslaray_date__gte=payfr_date,empslaray_date__lte=payto_date,emp_paidstatus=1,empreg_id__in=emp_reg.values_list('id', flat=True)).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
                            
                            
                            if sal_exp: 

                                if inexp:

                                    inexp.exin_head_name='SALARY'
                                    inexp.exin_amount=sal_exp
                                    inexp.exin_typ=2
                                    inexp.exin_date=payto_date
                                    inexp.exin_status=1
                                    inexp.exin_state=acc_state
                                    print('salary:',sal_exp)
                                    inexp.save()
                                                
                                else:

                                    incexp=IncomeExpence()
                                    incexp.exin_head_name='SALARY'
                                    incexp.exin_amount=sal_exp
                                    incexp.exin_typ=2
                                    incexp.exin_date=payto_date
                                    incexp.exin_status=1
                                    incexp.exin_state=acc_state
                                    print('salary:',sal_exp)
                                    incexp.save()
                            else:
                                print('No Data')

                        except EmployeeSalary.DoesNotExist:
                                print('No Data')

            except Company_Holidays.DoesNotExist:
                success_msg='Company Holiday not found add it.'

           
            emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
            emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,empstate=acc_state.state_name).exclude(id__in=emp_salary.values_list('empreg_id', flat=True))
            emp_reg_count=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,empstate=acc_state.state_name).exclude(id__in=emp_salary.values_list('empreg_id', flat=True)).count()
            
           
            content={'account_DHB':account_DHB,
                    'months':months,'years':years,
                    'emp_reg':emp_reg,
                    'emp_salary':emp_salary,
                    'current_year':current_year,
                    'emp_reg_count':emp_reg_count,
                    'acc_state':acc_state,'success_msg':success_msg}
            
            common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
            
            content = {**content, **common_accdash_data}
            return render(request,'account/salary_expence_form.html',content)

            
    else:
        return redirect('/')
    

def salary_calculate(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
    
        emp_reg=EmployeeRegister.objects.get(id=int(request.GET.get('persid'))) # Get the employee details

        # Here calculating the working days of selected month

        mon =int(request.GET.get('sm'))
        ye = int(request.GET.get('sy'))
           
        startdate = date(ye, mon, 1)
        last_day_of_month = startdate.replace(day=28) + timedelta(days=4)
        enddate = last_day_of_month - timedelta(days=last_day_of_month.day)
        month_days = (enddate - startdate).days + 1


            # Salary Calculations  
            
           

        try:

                comp_holiday=Company_Holidays.objects.get(ch_sdate__gte=startdate,ch_edate__lte=enddate)
              
              
                work_days=int(month_days) - int(comp_holiday.ch_no) 
                leavefull=int(request.GET.get('lf'))
                leavehalf=int(request.GET.get('lh'))
                w_delay=int(request.GET.get('wd'))
                any_other=int(request.GET.get('otamt'))
                any_dother=int(request.GET.get('otdamt'))

                if not leavefull:
                    leavefull=0
                if not leavehalf:
                    leavehalf=0
                if not w_delay:
                    w_delay=0
                if not any_other:
                    any_other=0
                if not any_dother:
                    any_dother=0

                conf_salary=emp_reg.empconfirmsalary
                one_day_salary=int(conf_salary / work_days)

                full_day_leave_amt=int(one_day_salary) * int(leavefull)
                half_day_leave_amt=int(one_day_salary / 2) * int(leavehalf)
                w_delay_amt=int(one_day_salary) * int(w_delay)
                net_salary=int(conf_salary) - int(full_day_leave_amt + half_day_leave_amt + w_delay_amt)
                net_salary=int(net_salary) + int(any_other)
                net_salary=int(net_salary) - int(any_dother)
                
               
                # Create a dictionary with the data you want to return
                response_data = {'net_salary': net_salary}

                # Return the response as a JSON object
                return JsonResponse(response_data, safe=False)
                
        except Company_Holidays.DoesNotExist:
               net_salary='Sorry ! Company holiday not found  '
               # Create a dictionary with the data you want to return
               response_data = {'net_salary': net_salary}

                # Return the response as a JSON object
               return JsonResponse(response_data, safe=False)
                
    else:
        return redirect('/')
    

def salary_expence_edit(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        
        

        emp_reg_edit=EmployeeSalary.objects.get(emp_paidstatus=1,id=pk)
        my=emp_reg_edit.empsalary_month
        mon_year = my.split()
       

        # Extract the first and second words
        if len(mon_year) == 2:
            mn = mon_year[0]
            ye = mon_year[1]
            date_obj = datetime.strptime(mn, '%B').date().replace(day=15)

               # Get the month number from the datetime.date object
            month_number = date_obj.month


        # content={'mn':mn,'ye':ye,'months':months,'years':years,'month_number':month_number}
       

        content={'account_DHB':account_DHB,
                    'months':months,'years':years,
                    'emp_reg_edit':emp_reg_edit,
                    'pay_month':mn,
                    'pay_year':ye,
                    'month_number':month_number,
                    'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
            
        content = {**content, **common_accdash_data}
        return render(request,'account/salary_expence_edit.html',content)


    else:
        return redirect('/')
    

    
def salary_edit_save(request,pk):
    
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------
    
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]

        current_year = datetime.now().year

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        
        
        if request.method =='POST':

            if request.POST['Emp_regid'] == '':

               return redirect('all_salary_expence')
            
            emp_reg=EmployeeRegister.objects.get(id=request.POST['Emp_regid']) # Get the employee details

            # Here calculating the working days of selected month

            mon =int(request.POST['empsalary_month'])
            ye = int(request.POST['empsalary_year'])
           
            startdate = date(ye, mon, 1)
            last_day_of_month = startdate.replace(day=28) + timedelta(days=4)
            enddate = last_day_of_month - timedelta(days=last_day_of_month.day)
            month_days = (enddate - startdate).days + 1


            # Salary Calculations  
            
           

            try:

                comp_holiday=Company_Holidays.objects.get(ch_sdate__gte=startdate,ch_edate__lte=enddate,ch_state=acc_state.id)
                work_days=int(month_days) - int(comp_holiday.ch_no) 
                leavefull=int(request.POST['leave_full'])
                leavehalf=int(request.POST['leave_half'])
                w_delay=int(request.POST['work_delay'])
                any_other=int(request.POST['other_amt'])
                any_dother=int(request.POST['other_damt'])

                if not request.POST['leave_full']:
                    leavefull=0
                if not request.POST['leave_half']:
                    leavehalf=0
                if not request.POST['work_delay']:
                    w_delay=0
                if not request.POST['other_amt']:
                    any_other=0
                if not request.POST['other_damt']:
                    any_dother=0

                conf_salary=emp_reg.empconfirmsalary
                one_day_salary=int(conf_salary / work_days)

                full_day_leave_amt=int(one_day_salary) * int(leavefull)
                half_day_leave_amt=int(one_day_salary / 2) * int(leavehalf)
                w_delay_amt=int(one_day_salary) * int(w_delay)
                net_salary=int(conf_salary) - int(full_day_leave_amt + half_day_leave_amt + w_delay_amt)
                net_salary=int(net_salary) + int(any_other)
                net_salary=int(net_salary) - int(any_dother)

                m = date(2000, int(request.POST['empsalary_month']), 1).strftime('%B')
                my = m + ' ' + request.POST['empsalary_year']

                if EmployeeSalary.objects.get(id=pk):
                    
                    emp_salary=EmployeeSalary.objects.get(id=pk)

                    total = int(emp_reg.emptol_salary) - int(emp_salary.emppaid_amt)
            
                    emp_reg.emptol_salary= int(total) + int(net_salary)
                    emp_reg.emp_salary_status=1
                    emp_reg.save()

                   
                    emp_salary.empreg_id=emp_reg
                
                    m = date(2000, int(request.POST['empsalary_month']), 1).strftime('%B')
                    
                    emp_salary.empsalary_month= m + ' ' + request.POST['empsalary_year']
                    
                    if request.POST['empsalary_date']:
                        emp_salary.empslaray_date=request.POST['empsalary_date']
                    else:
                        emp_salary.empslaray_date=emp_salary.empslaray_date

                    emp_salary.emppaid_amt= int(net_salary)
                    emp_salary.empfull_leave=leavefull
                    emp_salary.emphalf_leave=leavehalf
                    emp_salary.empfull_leave_amt=full_day_leave_amt
                    emp_salary.emphalf_leave_amt=half_day_leave_amt
                    emp_salary.emp_delay=w_delay
                    emp_salary.emp_delay_amt=w_delay_amt
                    emp_salary.emp_other_amt=any_other
                    emp_salary.emp_other_damt=any_dother
                    emp_salary.emp_paidstatus=1
                    emp_salary.save()
                    success_msg='Sucees! Salary Payment edit successfuly.'

                    # Salay Expence adding to IncomeExpence Table
                    if EmployeeSalary.objects.exists():
                        
                        if request.POST['empsalary_date']:

                            pay_date = datetime.strptime(request.POST['empsalary_date'], '%Y-%m-%d').date()
                        else:
                           pay_date= emp_salary.empslaray_date

                       
                        # Calculate start and end datetime objects for the month corresponding to input_date
                        payfr_date = pay_date.replace(day=1)

                        last_daymonth = payfr_date.replace(day=28) + timedelta(days=4)
                        payto_date = last_daymonth - timedelta(days=last_daymonth.day)

                        
                    
                        try:
                            inexp=IncomeExpence.objects.filter(exin_head_name='SALARY',exin_date__gte=payfr_date,exin_date__lte=payto_date,exin_state=acc_state).first()
                            emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date,empstate=acc_state.state_name)
                            sal_exp=EmployeeSalary.objects.filter(empslaray_date__gte=payfr_date,empslaray_date__lte=payto_date,emp_paidstatus=1,empreg_id__in=emp_reg.values_list('id', flat=True)).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
                            
                            
                            if sal_exp: 

                                if inexp:

                                    inexp.exin_head_name='SALARY'
                                    inexp.exin_amount=sal_exp
                                    inexp.exin_typ=2
                                    inexp.exin_date=payto_date
                                    inexp.exin_status=1
                                    inexp.exin_state=acc_state
                                    print('salary:',sal_exp)
                                    inexp.save()
                                                
                                else:

                                    incexp=IncomeExpence()
                                    incexp.exin_head_name='SALARY'
                                    incexp.exin_amount=sal_exp
                                    incexp.exin_typ=2
                                    incexp.exin_date=payto_date
                                    incexp.exin_status=1
                                    incexp.exin_state=acc_state
                                    print('salary:',sal_exp)
                                    incexp.save()
                            else:
                                print('No Data')

                        except EmployeeSalary.DoesNotExist:
                                print('No Data')

            except Company_Holidays.DoesNotExist:
                success_msg='Company Holiday not found add it.'

           
            
        emp_reg_edit=EmployeeSalary.objects.get(emp_paidstatus=1,id=pk)
        my=emp_reg_edit.empsalary_month
        mon_year = my.split()
       

        # Extract the first and second words
        if len(mon_year) == 2:
            mn = mon_year[0]
            ye = mon_year[1]
            date_obj = datetime.strptime(mn, '%B').date().replace(day=15)

               # Get the month number from the datetime.date object
            month_number = date_obj.month


        # content={'mn':mn,'ye':ye,'months':months,'years':years,'month_number':month_number}
       

        content={'account_DHB':account_DHB,
                    'months':months,'years':years,
                    'emp_reg_edit':emp_reg_edit,
                    'pay_month':mn,
                    'pay_year':ye,
                    'month_number':month_number,
                    'acc_state':acc_state,'success_msg':success_msg}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
            
        content = {**content, **common_accdash_data}
        return render(request,'account/salary_expence_edit.html',content)
            
           
           
            
    else:
        return redirect('/')
    

def salary_expence_remove(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        salary_remove=EmployeeSalary.objects.get(id=pk)
        emp_reg_edit=EmployeeRegister.objects.get(id=salary_remove.empreg_id.id)

        sal_pay_date = salary_remove.empslaray_date
    
        
        last_day_of_month = calendar.monthrange(sal_pay_date.year, sal_pay_date.month)[1]
        last_date = datetime(sal_pay_date.year, sal_pay_date.month, last_day_of_month).date() 

        

        remove_amount = int(salary_remove.emppaid_amt)
        emp_reg_edit.emptol_salary= int( emp_reg_edit.emptol_salary) - int(remove_amount)
        emp_reg_edit.save()

        inco_exp= IncomeExpence.objects.get(exin_head_name='SALARY',exin_state=acc_state,exin_date=last_date)

        inco_exp.exin_amount = int(inco_exp.exin_amount) -  int(remove_amount)
        inco_exp.save()

        salary_remove.delete()
        
        salary=EmployeeSalary.objects.filter(empreg_id=emp_reg_edit)
        salary_count=EmployeeSalary.objects.filter(empreg_id=emp_reg_edit).count()

        error_msg='Opps! Salary expence removed.'

        content={'account_DHB':account_DHB,
                    'emp_reg_edit':emp_reg_edit,
                    'salary':salary,
                    'salary_count':salary_count,
                    'acc_state':acc_state,'error_msg':error_msg}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/employee_salary_details.html',content)
    

    else:
        return redirect('/')
        
    
    
def all_salary_expence(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        
        emp_reg= EmployeeRegister.objects.filter(empstate=acc_state.state_name)
        salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1,empreg_id__in=emp_reg.values_list('id', flat=True)).order_by('-empslaray_date')
        salary_count=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1,empreg_id__in=emp_reg.values_list('id', flat=True)).count()
        salary_sum=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1,empreg_id__in=emp_reg.values_list('id', flat=True)).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']

        if request.method == 'POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']

            if sdate and edate:

                salary=EmployeeSalary.objects.filter(empslaray_date__gte=sdate,empslaray_date__lte=edate,emp_paidstatus=1,empreg_id__in=emp_reg.values_list('id', flat=True)).order_by('-empslaray_date')
                salary_count=EmployeeSalary.objects.filter(empslaray_date__gte=sdate,empslaray_date__lte=edate,emp_paidstatus=1,empreg_id__in=emp_reg.values_list('id', flat=True)).count()
                salary_sum=EmployeeSalary.objects.filter(empslaray_date__gte=sdate,empslaray_date__lte=edate,emp_paidstatus=1,empreg_id__in=emp_reg.values_list('id', flat=True)).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']


                
            else:
                return redirect('all_salary_expence')

        content={'account_DHB':account_DHB,
                                'salary':salary,
                                'salary_count':salary_count,
                                'salary_sum':salary_sum,
                                'acc_state':acc_state}
        
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/all_salary_expence.html',content)

    else:
        return redirect('/')
    
    
def Search_salary_payments(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
           uid = request.session['uid']
        else:
             return redirect('/')
        
        if request.method =='POST':
            salary=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=request.POST['spfr_data'],empslaray_date__lte=request.POST['spto_date']).order_by('empslaray_date')
        return render(request,'account/all_salary_expence.html',{'salary':salary})

    else:
        return redirect('/')





def employee_register_Details(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        dept=Department.objects.all()
        current_year = datetime.now().year
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]

        

        if request.method =='POST':
            emp_reg=EmployeeRegister()
            emp_reg.empfullName=request.POST['empname']
            emp_reg.empdept_id=Department.objects.get(id=request.POST['empdept'])
            emp_reg.empdofj=request.POST['empdfj']
            emp_reg.empdesignation=request.POST['empdesig'].upper()
            emp_reg.empidreg=request.POST['empid'].upper()
            emp_reg.empconfirmsalary=int(request.POST['empconf_salary'])
          
            emp_reg.emp_status=1
            emp_reg.emp_salary_status=1

            emp_reg.save()

            #emp_salary=EmployeeSalary()
            # emp_salary.empreg_id=emp_reg
          
            # m = date(2000, int(request.POST['empsalary_month']), 1).strftime('%B')
          
            # emp_salary.empsalary_month= str(m)+ ' ' + str(request.POST['empsalary_year']),
            # emp_salary.empslaray_date= request.POST['empsalary_date']
            # emp_salary.emppaid_amt= int(request.POST['empsalary_amt'])
            # emp_salary.emp_paidstatus=1
            #emp_salary.save()
          
            msg=1

            dept=Department.objects.filter(dpt_Status=1)
            emp_reg=EmployeeRegister.objects.all()

           
            
            return render(request,'account/Employee_Register.html',{'current_year':current_year,
                        'dept':dept,'emp_reg':emp_reg,'msg':msg,'months':months,'years':years})
        else:
            return redirect('emp_Register_form')
    else:
        return redirect('/')



    

def employee_register_Details_edit(request,pk):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            emp_reg=EmployeeRegister.objects.get(id=pk)
            emp_reg.empfullName=request.POST['empname']
            emp_reg.empdept_id=Department.objects.get(id=request.POST['empdept'])
            if request.POST['empdfj']:
                emp_reg.empdofj=request.POST['empdfj']
            else:
                emp_reg.empdofj= emp_reg.empdofj
            emp_reg.empdesignation=request.POST['empdesig'].upper()
            emp_reg.empidreg=request.POST['empid'].upper()
            emp_reg.empconfirmsalary=int(request.POST['empconf_salary'])
            
            emp_reg.emp_status=1
            emp_reg.emp_salary_status=1

            emp_reg.save()
            return redirect('emp_Register_form')
    else:
        return redirect('/')
        

    

def register_search(request):
        
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.method == 'POST':
        
            current_year = datetime.now().year
        
            months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
            years = [(str(i), str(i)) for i in range(2021, 2031)]
            
            dept=Department.objects.filter(dpt_Status=1)
        
            emp_reg=EmployeeRegister.objects.filter(empdofj__gte=request.POST['regfr_data'],empdofj__lte=request.POST['regto_date'])
            return render(request,'account/Employee_Register.html',{'current_year':current_year,'dept':dept,'emp_reg':emp_reg,'months':months,'years':years})
        else:
            return redirect('emp_Register_form')
        
    else:
        return redirect('/')
    

# Employee Account Active and Deactive---------------------

def emp_reg_active_deactive(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        emp_reg=EmployeeRegister.objects.get(id=pk)

        if emp_reg.emp_status == 0 :
            emp_reg.emp_status=1
            emp_reg.save()
            success_msg = "Success! Employee  Account Activated."

            reg_emp= EmployeeRegister.objects.filter(empstate=acc_state.state_name)
            reg_emp_count= EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()

        
            content={'account_DHB':account_DHB,
                        'acc_state':acc_state,
                        'reg_emp':reg_emp,
                        'reg_emp_count':reg_emp_count,
                        'success_msg':success_msg
                    }
        else:
            emp_reg.emp_status=0
            emp_reg.emp_salary_status=0
            emp_reg.save()
            error_msg= "Opps ! Employee  Account Deactivated."

            reg_emp= EmployeeRegister.objects.filter(empstate=acc_state.state_name)
            reg_emp_count= EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()

                

            content={'account_DHB':account_DHB,
                        'acc_state':acc_state,
                        'reg_emp':reg_emp,
                        'reg_emp_count':reg_emp_count,
                        'error_msg':error_msg
                    }
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas   
        content = {**content, **common_accdash_data}

        return render(request,'account/employee_list_page.html',content)
           
    else:
        return redirect('/')

# Employee Salary Account Active and Deactive---------------------       

def emp_salary_active_deactive(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        emp_reg=EmployeeRegister.objects.get(id=pk)

        if  emp_reg.emp_salary_status == 0:
            emp_reg.emp_salary_status=1
            emp_reg.save()

            success_msg = "Success! Employee salary account activated."

            reg_emp= EmployeeRegister.objects.filter(empstate=acc_state.state_name)
            reg_emp_count= EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()

        
            content={'account_DHB':account_DHB,
                        'acc_state':acc_state,
                        'reg_emp':reg_emp,
                        'reg_emp_count':reg_emp_count,
                        'success_msg':success_msg
                    }

        else:
            emp_reg.emp_salary_status=0
            emp_reg.save()

            error_msg= "Opps ! Employee salary account deactivated."

            reg_emp= EmployeeRegister.objects.filter(empstate=acc_state.state_name)
            reg_emp_count= EmployeeRegister.objects.filter(empstate=acc_state.state_name).count()

                

            content={'account_DHB':account_DHB,
                        'acc_state':acc_state,
                        'reg_emp':reg_emp,
                        'reg_emp_count':reg_emp_count,
                        'error_msg':error_msg
                    }


        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas   
        content = {**content, **common_accdash_data}

        return render(request,'account/employee_list_page.html',content)
           
    else:
        return redirect('/')
    


#Search Data using From Date and To Date 

def Search_data(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            
            payhis=PaymentHistory.objects.filter(paydofj__gte=request.POST['fr_data'],paydofj__lte=request.POST['to_date']).values_list('reg_id').distinct()
            cur_date=datetime.now().date()
        
            reg=Register.objects.filter(id__in=payhis)
        
            reg_count=Register.objects.all().count()
            dept_count=Department.objects.all().count()
            cur_date=datetime.now().date()
            pay_pending_count=PaymentHistory.objects.filter(admin_payconfirm=0).count()
        
            pay_count=Register.objects.filter(next_pay_date__lte=cur_date).count()
            content={'dept_count':dept_count,
                    'reg_count':reg_count,
                    'pay_count':pay_count,
                    'pay_pending_count':pay_pending_count}
            return render(request,'account/dashboard.html',{'reg':reg,'cur_date':cur_date,'content':content})
        
        else:
            return redirect('dashboard')
                
    else:
        return redirect('/')
        

    
def Search_data_full(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
            
        if request.method =='POST':
            payhis=PaymentHistory.objects.filter(paydofj__gte=request.POST['fr_data'],paydofj__lte=request.POST['to_date'])
            return render(request,'account/paymentsfull_View.html',{'payhis':payhis})
        else:
            return redirect('paymentfull_view')
            
    else:
        return redirect('/')
    
    

def employee_salary_details(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        

        account_DHB=Dashboard_Register.objects.get(id=uid) # Accountent Details Featch
        acc_state = Register_State.objects.get(allocate_dash=account_DHB) # Accountent state featch
        #-----------------------------------------------------------------------------

        emp_reg_edit=EmployeeRegister.objects.get(id=pk)
        salary=EmployeeSalary.objects.filter(empreg_id=pk).order_by('-empslaray_date')
        salary_count=EmployeeSalary.objects.filter(empreg_id=pk).count()

        if request.method =='POST':
            if request.POST['start_date'] and request.POST['end_date']:
                emp_reg_edit=EmployeeRegister.objects.get(id=pk)
                salary=EmployeeSalary.objects.filter(empreg_id=pk,empslaray_date__gte=request.POST['start_date'],empslaray_date__lte=request.POST['end_date']).order_by('-empslaray_date')
                salary_count=EmployeeSalary.objects.filter(empreg_id=pk,empslaray_date__gte=request.POST['start_date'],empslaray_date__lte=request.POST['end_date']).count()
            else:
                emp_reg_edit=EmployeeRegister.objects.get(id=pk)
                salary=EmployeeSalary.objects.filter(empreg_id=pk).order_by('-empslaray_date')
                salary_count=EmployeeSalary.objects.filter(empreg_id=pk).count()



        content={'account_DHB':account_DHB,
                    'emp_reg_edit':emp_reg_edit,
                    'salary':salary,
                    'salary_count':salary_count,
                    'acc_state':acc_state}
            
        common_accdash_data = account_nav_data(request,acc_state.id) # calling for navbar datas  
        
        content = {**content, **common_accdash_data}
        return render(request,'account/employee_salary_details.html',content)
        
    else:
        return redirect('/')
    


    


    


    

#============================== End Account Module ====================================================================



# ===========================Admin Module Section ======================================


# ----------------- Account Settings ---------------------------

def admin_account(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)


        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB}

        # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/Admin_Account.html',content)

    else:
            return redirect('/')


def admin_account_details_save(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)
        

        if request.method == 'POST':
            
            admin_DHB.dsh_name = request.POST['fname']
            admin_DHB.dsh_email = request.POST['email']
            admin_DHB.dsh_username = request.POST['uname'] 

            if request.FILES.get('profile_pic'):
                
                admin_DHB.dsh_image = request.FILES.get('profile_pic')
            else:
                admin_DHB.dsh_image = admin_DHB.dsh_image 

            admin_DHB.save()

            success_msg= 'Success! Profile Data Updated Successfully'
            admin_DHB=Dashboard_Register.objects.get(id=admid)

            content={'admin_DHB':admin_DHB,
                 'success_msg':success_msg }
            
        
        else:
            error_msg='Oops! Something Went Wrong'

            content={'admin_DHB':admin_DHB,
                 'error_msg':error_msg}

        common_data = nav_data(request)

            # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/Admin_Account.html',content)
           

    else:
            return redirect('/')


def admin_password_changeing(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)
        
        if request.method=='POST':

            oldpassword=request.POST['oldpsw']
            newpassword=request.POST['newpsw']

           
            if oldpassword == admin_DHB.dsh_password:

                admin_DHB.dsh_password=newpassword
                admin_DHB.save()

                success_msg= 'Success! Password Updated Successfully'
                admin_DHB=Dashboard_Register.objects.get(id=admid)

                content={'admin_DHB':admin_DHB,
                         'success_msg':success_msg,
                 
                 }
                
            
            else:

                error_msg = 'Opps! Old Password and New Password not maching'
                content={'admin_DHB':admin_DHB,
                 'error_msg':error_msg
                 }
            

        else:
                error_msg = 'Opps! Something Went Wrong'

                content={'admin_DHB':admin_DHB,
                 'error_msg':error_msg
                 }  

                
        
        common_data = nav_data(request)

            # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/Admin_Account.html',content)
        
    else:
        return redirect('/')


#---------------- End Account Settings -------------------------


def admin_dashboard(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')

        admin_DHB=Dashboard_Register.objects.get(id=admid)
        
        new_reg=Register.objects.filter(reg_status=0).count()
        


        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        #Income adding to IncomeExpence Table
        if PaymentHistory.objects.exists():
            try:
                inexpe=IncomeExpence.objects.filter(exin_head_name='OJT',exin_date__gte=fr_date,exin_date__lte=to_date).first()
                payhist=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
              
                
                if payhist:
                                
                    if inexpe:
                        inexpe.exin_head_name='OJT'
                        inexpe.exin_amount=payhist
                        inexpe.exin_typ=1
                        inexpe.exin_date=to_date
                        inexpe.exin_status=1
                        inexpe.save()

                    else:

                        incexpence=IncomeExpence()
                        incexpence.exin_head_name='OJT'
                        incexpence.exin_amount=payhist
                        incexpence.exin_typ=1
                        incexpence.exin_date=cur_date
                        incexpence.exin_status=1
                        incexpence.save()
                else:
                    print('No Data')

            except PaymentHistory.DoesNotExist:
                    print('No Data')
        else:
            print('No Data')
     


        # Salay Expence adding to IncomeExpence Table
        if EmployeeSalary.objects.exists():
            try:
                inexp=IncomeExpence.objects.filter(exin_head_name='SALARY',exin_date__gte=fr_date,exin_date__lte=to_date).first()
                sal_exp=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
                #sal_exp_last=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1).last()
                
                if sal_exp: 

                    if inexp:

                        inexp.exin_head_name='SALARY'
                        inexp.exin_amount=sal_exp
                        inexp.exin_typ=2
                        inexp.exin_date=to_date
                        inexp.exin_status=1
                        inexp.save()
                                    
                    else:

                        incexp=IncomeExpence()
                        incexp.exin_head_name='SALARY'
                        incexp.exin_amount=sal_exp
                        incexp.exin_typ=2
                        incexp.exin_date=cur_date
                        incexp.exin_status=1
                        incexp.save()
                else:
                    print('No Data')

            except EmployeeSalary.DoesNotExist:
                    print('No Data')
                            
        else:
            print('No Data')

        # Fixed Expence adding to the IncomeEpence Table

        active_sate=Register_State.objects.filter(allocate_status=1)

        for state in active_sate:

            fixexp=FixedExpence.objects.filter(fixed_date__lte=cur_date,fixed_date__gte=fr_date,fixed_status=1,fixed_state=state)
                            
            inex = IncomeExpence.objects.filter(exin_date__in=fixexp.values_list('fixed_date', flat=True),exin_state=state).filter(exin_head_name__in=fixexp.values_list('fixed_head_name', flat=True),exin_state=state)
            
            if inex:
                print('Data Found')

            else:

                not_in_inex = fixexp.exclude(fixed_date__in=inex.values_list('exin_date', flat=True)).exclude(fixed_head_name__in=inex.values_list('exin_head_name', flat=True)).values_list('id', flat=True)
                fixexp=FixedExpence.objects.filter(id__in=not_in_inex)
                for i in fixexp:
                    incomeexp = IncomeExpence()
                    incomeexp.exin_head_name=i.fixed_head_name
                    incomeexp.exin_date=i.fixed_date
                    incomeexp.exin_amount=i.fixed_amount
                    incomeexp.exin_typ=2
                    incomeexp.exin_state=state
                    incomeexp.exin_dese=i.fixed_dese
                    incomeexp.exin_status=1
                    incomeexp.save()
                    exp_date=i.fixed_date
                    today = date.today()

                    # Calculate the number of days in the current month
                    days_in_month = (today.replace(month=today.month+1, day=1) - timedelta(days=1)).day
                                
                    fr_date=exp_date + timedelta(days=days_in_month)
                    i.fixed_date=fr_date
                    i.save()

       

        common_data = nav_data(request)

        otj_reg = Register.objects.all().count()
        emp_reg = EmployeeRegister.objects.all().count()
        state_reg = Register_State.objects.filter(allocate_status=1).count()

        content={'admin_DHB':admin_DHB,
                 'new_reg':new_reg,
                 'otj_reg':otj_reg,
                 'emp_reg':emp_reg,
                 'state_reg':state_reg
                 }
        # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/Admin_dashboard.html',content)
    
    else:
        return redirect('/')
    


#============================Side Navbar Links =========================

# ============== State Section ================================

#state Register Form ------------------

def admin_state_form(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)
        
        depart = Department.objects.get(department='ACCOUNTS',dpt_Status=1)
        reg_emps = EmployeeRegister.objects.filter(empdept_id__id=depart.id)

        try:
            reg_states = Register_State.objects.filter(state_status=1).order_by('-id')
            reg_states_count = Register_State.objects.filter(state_status=1).count()

        except Register_State.DoesNotExist:

            reg_states=None
            reg_states_count=0
        
        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB,'reg_emps':reg_emps,'reg_states':reg_states,
                 'reg_states_count':reg_states_count
                 }
        # Merge the two dictionaries
        content = {**content, **common_data}
        
        return render(request,'Admin/admin_state_assign.html',content)
    else:
        return redirect('/')

#state Register  ------------------ 

def admin_state_register(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)
        
        depart = Department.objects.get(department='ACCOUNTS',dpt_Status=1)
        reg_emps = EmployeeRegister.objects.filter(empdept_id__id=depart.id)

        try:
            reg_states = Register_State.objects.filter(state_status=1)
            reg_states_count = Register_State.objects.filter(state_status=1).count()

        except Register_State.DoesNotExist:

            reg_states=None
            reg_states_count=0
        
        if request.method == 'POST':
            reg_state = Register_State()
            
            reg_state.state_name = request.POST['stateName']
           
            reg_state.state_status = 1
            reg_state.save()
            reg_state.state_id = f'ALTOS_STATE_0{reg_state.id}'
            reg_state.save()

            success_msg= 'Success! Your data has been processed successfully'

            reg_states = Register_State.objects.filter(state_status=1).order_by('-id')
            reg_states_count = Register_State.objects.filter(state_status=1).count()

            common_data = nav_data(request)

            content={'admin_DHB':admin_DHB,'reg_emps':reg_emps,'reg_states':reg_states,
                     'reg_states_count':reg_states_count,
                     'success_msg':success_msg}
            
            # Merge the two dictionaries
            content = {**content, **common_data}

            return render(request,'Admin/admin_state_assign.html',content)

        else:
            common_data = nav_data(request)
            error_msg= 'Opps! Something went wrong'
            content={'admin_DHB':admin_DHB,'reg_emps':reg_emps,'reg_states':reg_states,
                     'reg_states_count':reg_states_count,
                     'error_msg':error_msg}
            
            # Merge the two dictionaries
            content = {**content, **common_data}

            return render(request,'Admin/admin_state_assign.html',content)

    else:
        return redirect('/')


#state Register Allocation ------------------

def admin_state_allocation(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)
        
        depart = Department.objects.get(department='ACCOUNTS',dpt_Status=1)
        reg_emps = EmployeeRegister.objects.filter(empdept_id__id=depart.id)

        try:
            reg_states = Register_State.objects.filter(state_status=1)
            reg_states_count = Register_State.objects.filter(state_status=1).count()

        except Register_State.DoesNotExist:

            reg_states=None
            reg_states_count=0
        
        if request.method == 'POST':


            reg_state = Register_State.objects.get(id=int(request.POST['state_rowid']))
            
            emp = EmployeeRegister.objects.get(id=int(request.POST['empName']))
            reg_state.allocateid = emp
            
            reg_state.allocate_status = 1
            reg_state.save()

            #Dashboard creation

            dashb = Dashboard_Register()
            dashb.dsh_name = emp.empfullName
            dashb.dsh_email = emp.empemail
            dashb.dsh_username = reg_state.state_id
            dashb.dsh_password = reg_state.state_id
            dashb.active_status = 2
            dashb.save()

            reg_state.allocate_dash = dashb
            reg_state.save()
            
            success_msg= 'Success! State allocated successfully'

            reg_states = Register_State.objects.filter(state_status=1).order_by('-id')
            reg_states_count = Register_State.objects.filter(state_status=1).count()

            common_data = nav_data(request)

            content={'admin_DHB':admin_DHB,'reg_emps':reg_emps,'reg_states':reg_states,
                        'reg_states_count':reg_states_count,
                        'success_msg':success_msg}
            
            # Merge the two dictionaries
            content = {**content, **common_data}

            return render(request,'Admin/admin_state_assign.html',content)

        else:
            common_data = nav_data(request)
            error_msg= 'Opps! Something went wrong'
            content={'admin_DHB':admin_DHB,'reg_emps':reg_emps,'reg_states':reg_states,
                     'reg_states_count':reg_states_count,
                     'error_msg':error_msg}
            # Merge the two dictionaries
            content = {**content, **common_data}

            return render(request,'Admin/admin_state_assign.html',content)

    else:
        return redirect('/')


#state Register Reallocation ----------------

def admin_state_reallocation(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)

        depart = Department.objects.get(department='ACCOUNTS',dpt_Status=1)
        reg_emps = EmployeeRegister.objects.filter(empdept_id__id=depart.id)

        try:
            reg_states = Register_State.objects.filter(state_status=1)
            reg_states_count = Register_State.objects.filter(state_status=1).count()

        except Register_State.DoesNotExist:

            reg_states=None
            reg_states_count=0
        
        if request.method == 'POST':

            reg_state = Register_State.objects.get(id=int(request.POST['restate_rowid']))
            
            emp = EmployeeRegister.objects.get(id=int(request.POST['re-allocateName']))
            reg_state.allocateid = emp 
            
            reg_state.allocate_status = 1
            reg_state.save()

            dashb = Dashboard_Register.objects.get(id=reg_state.allocate_dash.id)
            dashb.dsh_name = emp.empfullName
            dashb.dsh_email = emp.empemail
            dashb.dsh_username = reg_state.state_id
            dashb.dsh_password = reg_state.state_id
            dashb.active_status = 2
            dashb.save()
            
            success_msg= 'Success! State Re-allocated successfully'

            reg_states = Register_State.objects.filter(state_status=1).order_by('-id')
            reg_states_count = Register_State.objects.filter(state_status=1).count()

            common_data = nav_data(request)

            content={'admin_DHB':admin_DHB,'reg_emps':reg_emps,'reg_states':reg_states,
                        'reg_states_count':reg_states_count,
                        'success_msg':success_msg}
            # Merge the two dictionaries
            content = {**content, **common_data}

            return render(request,'Admin/admin_state_assign.html',content)

        else:
            common_data = nav_data(request)
            error_msg= 'Opps! Something went wrong'
            content={'admin_DHB':admin_DHB,'reg_emps':reg_emps,'reg_states':reg_states,
                     'reg_states_count':reg_states_count,
                     'error_msg':error_msg}
            # Merge the two dictionaries
            content = {**content, **common_data}

            return render(request,'Admin/admin_state_assign.html',content)

    else:
        return redirect('/')


# ==============End State Section ==============================





def newpay_confirm_list(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)
        #------------------------------------------------
 
            
        reg=Register.objects.filter(reg_status=0)
        new_reg_count = Register.objects.filter(reg_status=0).count()
        firstpayhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg).first
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg)
        
        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB,
                 'payhis':payhis,
                 'firstpayhis':firstpayhis,
                 'new_reg_count':new_reg_count}

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/newpayment_list.html',content)
            
    else:
        return redirect('/')


def admin_trackPayments(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #------------------------------------------------

        if request.method=='POST':

            if request.POST['search_select'] == '0':
                
                up_payments = upcoming_payments(request)
            
            else:
                state_id=Register_State.objects.get(id=int(request.POST['search_select']))
                up_payments = upcoming_state_payments(request,state_id)   
        
        else:

            up_payments = upcoming_payments(request)


        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB}
            # Merge the two dictionaries
        content = {**content, **common_data, **up_payments}

        return render(request,'Admin/admintrack_Payments.html',content)
    
    else:
        return redirect('/')
    

def adminquick_search(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        

        # Date 1 to 1 Days
        if pk == 0:
            cur_date=datetime.now().date()
            sdate=datetime(cur_date.year, cur_date.month, 1).date()
            edate = sdate + timedelta(days=6)
            reg=Register.objects.filter(next_pay_date__gte=sdate,next_pay_date__lte=edate,payment_status=0)
            reg_count=Register.objects.filter(next_pay_date__gte=sdate,next_pay_date__lte=edate,payment_status=0).count()
            tk_amount=0
            for i in reg:
                tk_amount=tk_amount + int(i.next_pat_amt)

            content={'fr_date':sdate,
                    'to_date':edate,
                    'reg_count':reg_count,
                    'tk_amount':tk_amount,
                    'cur_date':cur_date
                    }
            return render(request,'Admin/admintrack_Payments.html',{'reg':reg,'content':content})
        
        # Date 8 to 15 Days
        elif pk == 1:
            
            cur_date=datetime.now().date()
            sdate=datetime(cur_date.year, cur_date.month, 8).date()
            edate = sdate + timedelta(days=7)

            reg=Register.objects.filter(next_pay_date__gte=sdate,next_pay_date__lte=edate,payment_status=0)
            reg_count=Register.objects.filter(next_pay_date__gte=sdate,next_pay_date__lte=edate,payment_status=0).count()
            tk_amount=0
            for i in reg:
                tk_amount=tk_amount + int(i.next_pat_amt)

            content={'fr_date':sdate,
                    'to_date':edate,
                    'reg_count':reg_count,
                    'tk_amount':tk_amount,
                    'cur_date':cur_date
                    }
            return render(request,'Admin/admintrack_Payments.html',{'reg':reg,'content':content})
        
        # Date 16 to end of the  Current month 
        elif pk == 2:

            cur_date=datetime.now().date()
            sdate=datetime(cur_date.year, cur_date.month, 16).date()
            last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
            edate = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

            reg=Register.objects.filter(next_pay_date__gte=sdate,next_pay_date__lte=edate,payment_status=0)
            reg_count=Register.objects.filter(next_pay_date__gte=sdate,next_pay_date__lte=edate,payment_status=0).count()

            tk_amount=0
            for i in reg:
                tk_amount=tk_amount + int(i.next_pat_amt)

            content={'fr_date':sdate,
                    'to_date':edate,
                    'reg_count':reg_count,
                    'tk_amount':tk_amount,
                    'cur_date':cur_date
                    }
            return render(request,'Admin/admintrack_Payments.html',{'reg':reg,'content':content})

        else:
            return redirect('admin_trackPayments')
            
    else:
        return redirect('/')



def adminupcomingPayments(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            sdate=request.POST['start_date']
            edate=request.POST['end_date']
            cur_date=datetime.now().date()
            reg=Register.objects.filter(next_pay_date__gte=sdate,next_pay_date__lte=edate,payment_status=0)
            reg_count=Register.objects.filter(next_pay_date__gte=sdate,next_pay_date__lte=edate,payment_status=0).count()
            tk_amount=0
            for i in reg:
                tk_amount=tk_amount + int(i.next_pat_amt)

            content={'fr_date':sdate,
                    'to_date':edate,
                    'reg_count':reg_count,
                    'tk_amount':tk_amount,
                    'cur_date':cur_date
                    }
            return render(request,'Admin/admintrack_Payments.html',{'reg':reg,'content':content})
        else:
            return redirect('admin_trackPayments')  
            
    else:
        return redirect('/')
    


def admin_paymentsview(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------

        reg=Register.objects.all()
        payhis_count=PaymentHistory.objects.all().count()

        if request.method=='POST':

            sdate= request.POST['start_date']
            edate= request.POST['end_date']
            
            if request.POST['search_select'] == '0' and sdate and edate:
              
                reg=Register.objects.filter(dofj__gte=sdate,dofj__lte=edate)
               

            elif request.POST['search_select'] and sdate and edate:
               
               state = Register_State.objects.get(id=int(request.POST['search_select']))
               reg=Register.objects.filter(dofj__gte=sdate,dofj__lte=edate,reg_state=state)
              
            
            elif request.POST['search_select'] != '0' :
                state = Register_State.objects.get(id=int(request.POST['search_select']))
                reg=Register.objects.filter(reg_state=state)

            else:
                reg=Register.objects.all()
                

           
        payhis_count=PaymentHistory.objects.filter(reg_id__in=reg).count()
        payhis=PaymentHistory.objects.all()

        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'reg':reg,'payhis':payhis,
                   'payhis_count':payhis_count,
                  
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/adminpayments_history.html',content)
            
    else:
        return redirect('/')



def adminpaymentfull_view(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
            
        payhis=PaymentHistory.objects.all()
        return render(request,'Admin/adminpaymentsfull_View.html',{'payhis':payhis})
            
    else:
        return redirect('/')
    


def adminsearch_data_full(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            payhis=PaymentHistory.objects.filter(paydofj__gte=request.POST['fr_data'],paydofj__lte=request.POST['to_date'])
            return render(request,'Admin/adminpaymentsfull_View.html',{'payhis':payhis})
        else:
            return redirect('adminpaymentfull_view')
            
    else:
        return redirect('/')




def view_details(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)



        
        reg=Register.objects.filter(reg_status=0)
        firstpayhis=PaymentHistory.objects.get(id=pk)
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg)

        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB,'payhis':payhis,'firstpayhis':firstpayhis}

        # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/newpayment_list.html',content)
            
    else:
        return redirect('/')
    


def admin_approve(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)
        #--------------------------------------------------
        
        pay_aprove=PaymentHistory.objects.get(id=pk)
        pay_aprove.admin_payconfirm=1
        pay_aprove.pay_status=1
        pay_aprove.save()

        payed_date=pay_aprove.paydofj # Getting the payed date to add the OJT amount to Income Expence table 

        reg=Register.objects.get(id=pay_aprove.reg_id_id)
        reg.regbalance_amt= int(reg.regtotal_amt - pay_aprove.payintial_amt)
        pay_aprove.paybalance_amt=int( reg.regbalance_amt)
        pay_aprove.save()
        reg.reg_payedtotal=int(pay_aprove.payintial_amt)
        reg.reg_status=1

        pay_aprove.paytotal_amt=int(reg.reg_payedtotal)
        pay_aprove.save()

        #next payment calculation

        cal=int(reg.fixed_intial_amt)
        
        if cal == pay_aprove.payintial_amt:
            reg.next_pat_amt = int( reg.regbalance_amt / 2)
            reg.fixed_intial_amt = int( reg.regbalance_amt / 2)

        elif cal >  pay_aprove.payintial_amt:
            reg.next_pat_amt =  int(cal) - int(pay_aprove.payintial_amt)
            reg.fixed_intial_amt = int( reg.regbalance_amt / 2)

        elif  cal <  pay_aprove.payintial_amt:
             
            reg.next_pat_amt = int( reg.regbalance_amt / 2)
            reg.fixed_intial_amt = int( reg.regbalance_amt / 2)

        else:
            print('error')


        if reg.regbalance_amt <= 0:
            reg.next_pay_date=None
            reg.next_pat_amt = 0
            reg.payment_status=1
            reg.payprogress=100
        reg.save()

        #calculating the starting date and ending date of OJT amount payed 

        fr_date = payed_date.replace(day=1)
        last_daymonth = fr_date.replace(day=28) + timedelta(days=4)
        to_date = last_daymonth - timedelta(days=last_daymonth.day)

        #Income adding to IncomeExpence Table
        if PaymentHistory.objects.exists():

            try:

                inexpe=IncomeExpence.objects.filter(exin_head_name='OJT',exin_date__gte=fr_date,exin_date__lte=to_date,exin_state=pay_aprove.pay_state).first()
                payhist=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1,pay_state=pay_aprove.pay_state).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
         
                
                if payhist:
                                
                    if inexpe:
                        inexpe.exin_head_name='OJT'
                        inexpe.exin_amount=payhist
                        inexpe.exin_typ=1
                        inexpe.exin_date=to_date
                        inexpe.exin_status=1
                        inexpe.exin_state=pay_aprove.pay_state
                        inexpe.save()

                    else:

                        incexpence=IncomeExpence()
                        incexpence.exin_head_name='OJT'
                        incexpence.exin_amount=payhist
                        incexpence.exin_typ=1
                        incexpence.exin_date=to_date
                        incexpence.exin_status=1
                        incexpence.exin_state=pay_aprove.pay_state
                        incexpence.save()
                else:
                    print('No Data')

            except PaymentHistory.DoesNotExist:
                    print('No Data')
        else:
            print('No Data')
     

        success_msg="Success! OJT Registration successfull."

        reg=Register.objects.filter(reg_status=0)
        new_reg_count = Register.objects.filter(reg_status=0).count()
        firstpayhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg).first
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg)
        
        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB,
                 'payhis':payhis,
                 'firstpayhis':firstpayhis,
                 'new_reg_count':new_reg_count,
                 'success_msg':success_msg}

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/newpayment_list.html',content)
            
    else:
        return redirect('/')
    


def admin_confirm(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)
            
        pay_aprove=PaymentHistory.objects.get(id=pk)
        pay_aprove.admin_payconfirm=1
        pay_aprove.pay_status=1
        pay_aprove.save()

        reg=Register.objects.get(id=pay_aprove.reg_id_id)
        reg.regbalance_amt= int(reg.regbalance_amt - pay_aprove.payintial_amt)
        paytol=int( reg.reg_payedtotal)+int(pay_aprove.payintial_amt)
        reg.reg_payedtotal=paytol
        progres=int((paytol  * 100) / reg.regtotal_amt)
        
        reg.payprogress=progres
        reg.save()

       
        
        if reg.fixed_intial_amt == pay_aprove.payintial_amt:
            reg.next_pat_amt = int(reg.regbalance_amt)
            reg.fixed_intial_amt = int(reg.regbalance_amt)

        elif reg.fixed_intial_amt >  pay_aprove.payintial_amt:
           
            reg.next_pat_amt = int(reg.fixed_intial_amt) - int(pay_aprove.payintial_amt)
            reg.fixed_intial_amt = int(reg.fixed_intial_amt) - int(pay_aprove.payintial_amt)

        elif  reg.fixed_intial_amt <  pay_aprove.payintial_amt:
           
            reg.next_pat_amt = int(reg.regbalance_amt)
            reg.fixed_intial_amt = int(reg.regbalance_amt)

        else:
            print('error')

        reg.save()

        if reg.regbalance_amt <= 0:
            reg.next_pay_date=None
            reg.payment_status=1
            reg.next_pat_amt = 0
            reg.save()

        pay_aprove.paybalance_amt= int(reg.regbalance_amt)
        pay_aprove.paytotal_amt=int(reg.reg_payedtotal)
        pay_aprove.save()

        payed_date = pay_aprove.paydofj
        
        #calculating the starting date and ending date of OJT amount payed 

        fr_date = payed_date.replace(day=1)
        last_daymonth = fr_date.replace(day=28) + timedelta(days=4)
        to_date = last_daymonth - timedelta(days=last_daymonth.day)

        #Income adding to IncomeExpence Table
        if PaymentHistory.objects.exists():
            try:
                inexpe=IncomeExpence.objects.filter(exin_head_name='OJT',exin_date__gte=fr_date,exin_date__lte=to_date).first()
                payhist=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
                #payhi_last=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).last()
                
                if payhist:
                                
                    if inexpe:
                        inexpe.exin_head_name='OJT'
                        inexpe.exin_amount=payhist
                        inexpe.exin_typ=1
                        inexpe.exin_date=to_date
                        inexpe.exin_status=1
                        inexpe.save()

                    else:

                        incexpence=IncomeExpence()
                        incexpence.exin_head_name='OJT'
                        incexpence.exin_amount=payhist
                        incexpence.exin_typ=1
                        incexpence.exin_date=to_date
                        incexpence.exin_status=1
                        incexpence.save()
                else:
                    print('No Data')

            except PaymentHistory.DoesNotExist:
                    print('No Data')
        else:
            print('No Data')


        return redirect('admin_dashboard')
     
        
    else:
        return redirect('/')
    


def admin_remove(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB=Dashboard_Register.objects.get(id=admid)

        payhis=PaymentHistory.objects.get(id=pk)
        reg=Register.objects.get(id=payhis.reg_id.id)
        payhis.delete()
        reg.delete()

        error_msg="Opps! Registration data and Payment data are removed."

        reg=Register.objects.filter(reg_status=0)
        new_reg_count = Register.objects.filter(reg_status=0).count()
        firstpayhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg).first
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg)
        
        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB,
                 'payhis':payhis,
                 'firstpayhis':firstpayhis,
                 'new_reg_count':new_reg_count,
                 'error_msg':error_msg}

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/newpayment_list.html',content)
            
    else:
        return redirect('/')




def admin_user_list(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        dept=Department.objects.all()
        reg=Register.objects.all()

        try:
            editreg=Register.objects.all().first()
        
        except Register.DoesNotExist:
            editreg=None
            return redirect('admin_dashboard')

        return render(request,'Admin/users_list.html',{'editreg':editreg,'reg':reg,'dept':dept})
            
    else:
        return redirect('/')


def admin_allpayments_list(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        reg=Register.objects.all()
        cur_date=datetime.now().date()
        return render(request,'Admin/adminallpaymets.html',{'reg':reg,'cur_date':cur_date})
            
    else:
        return redirect('/')


def admin_pending_payments(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #----------------------------------------------------

        if request.method=='POST':
            if request.POST['search_select'] == '0':

                pay_reg=Register.objects.filter(payment_status=0)
                pay_reg_count=Register.objects.filter(payment_status=0).count()
                pay_amt=Register.objects.filter(payment_status=0).aggregate(Sum('regbalance_amt'))

               

            else:

                state_id=Register_State.objects.get(id=int(request.POST['search_select']))

              

                #pending payment
                pay_reg=Register.objects.filter(payment_status=0,reg_state=state_id)
                pay_reg_count=Register.objects.filter(payment_status=0).count()
                pay_amt=Register.objects.filter(payment_status=0,reg_state=state_id).aggregate(Sum('regbalance_amt'))

               
        else:
        
           
            pay_reg=Register.objects.filter(payment_status=0)
            pay_reg_count=Register.objects.filter(payment_status=0).count()
            pay_amt=Register.objects.filter(payment_status=0).aggregate(Sum('regbalance_amt'))

           

        common_data = nav_data(request)

        head_name = 'Pending' 

        cur_date=datetime.now().date()
        
        content={'admin_DHB':admin_DHB,
                 'pay_reg':pay_reg,
                 'pay_reg_count':pay_reg_count,
                 'payamt':pay_amt,
                 'head_name':head_name,'cur_date':cur_date
                 }
            # Merge the two dictionaries
        content = {**content, **common_data}
        return render(request,'Admin/adminallpaymets.html',content)
            
    else:
        return redirect('/')
    

def admin_completed_payments(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #----------------------------------------------------

        if request.method=='POST':
            if request.POST['search_select'] == '0':

               
                pay_reg=Register.objects.filter(payment_status=1)
                pay_reg_count=Register.objects.filter(payment_status=1).count()
                pay_amt=Register.objects.filter(payment_status=1).aggregate(Sum('regtotal_amt'))

   
            else:

                state_id=Register_State.objects.get(id=int(request.POST['search_select']))

                
                pay_reg=Register.objects.filter(payment_status=1,reg_state=state_id)
                pay_reg_count=Register.objects.filter(payment_status=1,reg_state=state_id).count()
                pay_amt=Register.objects.filter(payment_status=1,reg_state=state_id).aggregate(Sum('regtotal_amt'))

               
        else:
        
           

            pay_reg=Register.objects.filter(payment_status=1)
            pay_reg_count=Register.objects.filter(payment_status=1).count()
            pay_amt=Register.objects.filter(payment_status=1).aggregate(Sum('regtotal_amt'))

           

        common_data = nav_data(request)

        head_name = 'Completed'

        content={'admin_DHB':admin_DHB,
                 'pay_reg':pay_reg,
                 'pay_reg_count':pay_reg_count,
                 'payamt':pay_amt,
                 'head_name':head_name
                 }
            # Merge the two dictionaries
        content = {**content, **common_data}
        
        return render(request,'Admin/adminallpaymets.html',content)
            
    else:
        return redirect('/')
    


def admin_incompleted_payments(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #----------------------------------------------------

        if request.method=='POST':
            if request.POST['search_select'] == '0':


                pay_reg=Register.objects.filter(payment_status=2)
                pay_reg_count=Register.objects.filter(payment_status=2).count()
                pay_amt=Register.objects.filter(payment_status=2).aggregate(Sum('regtotal_amt'))


            else:

                state_id=Register_State.objects.get(id=int(request.POST['search_select']))

               
                pay_reg=Register.objects.filter(payment_status=2,reg_state=state_id)
                pay_reg_count=Register.objects.filter(payment_status=2,reg_state=state_id).count()
                pay_amt=Register.objects.filter(payment_status=2,reg_state=state_id).aggregate(Sum('regtotal_amt'))
        else:
        
           
            pay_reg=Register.objects.filter(payment_status=2)
            pay_reg_count=Register.objects.filter(payment_status=2).count()
            pay_amt=Register.objects.filter(payment_status=2).aggregate(Sum('regtotal_amt'))

        common_data = nav_data(request)

        head_name = 'Incompleted'

        content={'admin_DHB':admin_DHB,
                 'pay_reg':pay_reg,
                 'pay_reg_count':pay_reg_count,
                 'payamt':pay_amt,
                 'head_name':head_name
                 }
            # Merge the two dictionaries
        content = {**content, **common_data}
        return render(request,'Admin/adminallpaymets.html',content)
            
    else:
        return redirect('/')
    

def adminpaysearch(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
            
        if request.method =='POST':
            
            payhis=PaymentHistory.objects.filter(paydofj__gte=request.POST['adpfr_data'],paydofj__lte=request.POST['adpto_date']).values_list('reg_id').distinct()
            cur_date=datetime.now().date()
        
            reg=Register.objects.filter(id__in=payhis)
            return render(request,'Admin/adminallpaymets.html',{'reg':reg,'cur_date':cur_date})
        else:
            return redirect('admin_allpayments_list')
        
    else:
        return redirect('/')
    

def admin_department_form(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        # content load to base page
        states = Register_State.objects.filter(allocate_status=1)
        reg1=Register.objects.filter(reg_status=1)
        approvels=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1)
        approve_count=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1).count()
        #------------------------------

        dept=Department.objects.all().order_by('-id')
        dept_count=Department.objects.all().count()

        content={'dept':dept,
                     'states':states,
                     'approvels':approvels,
                     'approve_count':approve_count,
                     'dept_count':dept_count,
                     }
        return render(request,'Admin/admin_department_form.html',content)
        
    else:
        return redirect('/')
    

def admin_department_add(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        states = Register_State.objects.filter(allocate_status=1)
        reg1=Register.objects.filter(reg_status=1)
        approvels=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1)
        approve_count=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1).count()
        
        if request.method =='POST':  
            dept=Department()
            dept.department=request.POST['dept_name'].upper()
            dept.dpt_Status=1
            dept.save()
            success_msg= 'Success! New department data has been saved'
            dept=Department.objects.all().order_by('-id')
            dept_count=Department.objects.all().count()
            
            content={'dept':dept,
                     'success_msg':success_msg,
                     'states':states,
                     'approvels':approvels,
                     'approve_count':approve_count,
                     'dept_count':dept_count,
                     }
            return render(request,'Admin/admin_department_form.html',content)
        else:
            error_msg= 'Opps! Something went wrong'
            
            content={'dept':dept,
                     'error_msg':error_msg,
                     'states':states,
                     'approvels':approvels,
                     'approve_count':approve_count,
                     'dept_count':dept_count,
                     }
        
            return render(request,'Admin/admin_department_form.html',content)
        
    else:
        return redirect('/')
    
def admin_edit_dept(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
          
        dept_edit=Department.objects.get(id=pk)
      
        dept=Department.objects.all().order_by('-id')
        return render(request,'Admin/admin_department_form.html',{'dept':dept,'dept_edit':dept_edit})
    
    else:
        return redirect('/')
          
    
def admin_remove_dept(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        states = Register_State.objects.filter(allocate_status=1)
        reg1=Register.objects.filter(reg_status=1)
        approvels=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1)
        approve_count=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1).count()
        
          
        depart=Department.objects.get(id=pk)
        depart.delete()
        error_msg= 'Opps! Department data has been removed'

        dept=Department.objects.all().order_by('-id')
        dept_count=Department.objects.all().count()
        
        content={'dept':dept,
                     'error_msg':error_msg,
                     'states':states,
                     'approvels':approvels,
                     'approve_count':approve_count,
                     'dept_count':dept_count,
                     }
        
        return render(request,'Admin/admin_department_form.html',content)
        
    else:
        return redirect('/')



# Admin Accounts Section 

def admin_accounts(request):
    
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        in_ex_count=IncomeExpence.objects.filter(exin_date__gte=fr_date,exin_date__lte=to_date).count()
        fixed_ex_count=FixedExpence.objects.all().count()
        

        income=IncomeExpence.objects.filter(exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        expence=IncomeExpence.objects.filter(exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        if not income:
            income=1
        if not expence:
            expence=1
        balans=int(income) -int(expence)
        
        bal_p= income - expence 
        if bal_p < 0:
            
            bal_p=-(bal_p)
        
        exp_pr=int(expence) / int(bal_p + income + expence)
        inc_pr=int(income) / int(bal_p + income + expence)
        bal_pr=int(bal_p) / int(bal_p + income + expence)
        
        

       
        emp_reg_count=EmployeeRegister.objects.filter(emp_status=1).count()
        emp_salary_count=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empdofj__lt=fr_date).count()
        content={'emp_reg_count':emp_reg_count,
                 'emp_salary_count':emp_salary_count,
                 'income':income,
                 'expence':expence,
                 'balans':balans,
                 'inc_pr':inc_pr,
                 'exp_pr':exp_pr,
                 'in_ex_count':in_ex_count,
                 'fixed_ex_count':fixed_ex_count,'bal_pr':bal_pr
                 
                 }
        return render(request,'Admin/admin_accounts.html',{'content':content})
        
    else:
            return redirect('/')
    

def admin_emp_Register_view(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------
        emp_reg=EmployeeRegister.objects.all()
        emp_reg_count=EmployeeRegister.objects.all().count()

        if request.method == 'POST':

            sdate= request.POST['start_date']
            edate= request.POST['end_date']
            
            if request.POST['search_select']=='0' and sdate and edate :

                emp_reg=EmployeeRegister.objects.filter(empdofj__gte=sdate,empdofj__lte=edate)
                emp_reg_count=EmployeeRegister.objects.filter(empdofj__gte=sdate,empdofj__lte=edate).count()

            elif request.POST['search_select'] and sdate and edate :

                state = Register_State.objects.get(id=int(request.POST['search_select']))
                emp_reg=EmployeeRegister.objects.filter(empdofj__gte=sdate,empdofj__lte=edate,empstate=state.state_name)
                emp_reg_count=EmployeeRegister.objects.filter(empdofj__gte=sdate,empdofj__lte=edate,empstate=state.state_name).count()
            
            elif request.POST['search_select'] !='0':

                state = Register_State.objects.get(id=int(request.POST['search_select']))
                emp_reg=EmployeeRegister.objects.filter(empstate=state.state_name)
                emp_reg_count=EmployeeRegister.objects.filter(empstate=state.state_name).count()

            else:
                emp_reg=EmployeeRegister.objects.all()
                emp_reg_count=EmployeeRegister.objects.all().count()

        

        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'emp_reg':emp_reg,'emp_reg_count':emp_reg_count
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}
        return render(request,'Admin/admin_Employee_view.html',content)
        
    else:
            return redirect('/')
    

def admin_register_search(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.method == 'POST':
        
            emp_reg=EmployeeRegister.objects.filter(empdofj__gte=request.POST['adregfr_data'],empdofj__lte=request.POST['adregto_date'])
            return render(request,'Admin/admin_Employee_view.html',{'emp_reg':emp_reg})
        else:
            return redirect('admin_emp_Register_view')
        
    else:
            return redirect('/')
    

def admin_income_expence(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        
        exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('-id')
        exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=fr_date,exin_date__lte=to_date).count()
        inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(intol=Sum('exin_amount'))['intol']
        expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(exptol=Sum('exin_amount'))['exptol']
        

       

        if request.method == 'POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']


            if request.POST['search_select'] == '0' and sdate and edate :
                 
                exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=sdate,exin_date__lte=edate).order_by('-id')
                exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=sdate,exin_date__lte=edate).count()

                inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_date__gte=sdate,exin_date__lte=edate).aggregate(intol=Sum('exin_amount'))['intol']
                expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_date__gte=sdate,exin_date__lte=edate).aggregate(exptol=Sum('exin_amount'))['exptol']
                
                
       
            elif request.POST['search_select'] and sdate and edate :

                state = Register_State.objects.get(id=int(request.POST['search_select']))
                exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=sdate,exin_date__lte=edate,exin_state=state).order_by('-id')
                exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=sdate,exin_date__lte=edate,exin_state=state).count()

                inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_date__gte=sdate,exin_date__lte=edate,exin_state=state).aggregate(intol=Sum('exin_amount'))['intol']
                expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_date__gte=sdate,exin_date__lte=edate,exin_state=state).aggregate(exptol=Sum('exin_amount'))['exptol']
               
            
            elif  request.POST['search_select'] != '0':

                state = Register_State.objects.get(id=int(request.POST['search_select']))
                exp_income=IncomeExpence.objects.filter(exin_status=1,exin_state=state).order_by('-id')
                exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_state=state).count()

                inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_state=state).aggregate(intol=Sum('exin_amount'))['intol']
                expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_state=state).aggregate(exptol=Sum('exin_amount'))['exptol']
               
            
            else:
                exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('-id')
                exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=fr_date,exin_date__lte=to_date).count()

       
        if expe == None:
           expe=0
        if inco == None:
           inco=0

        balans=inco-expe
    
        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                  'exp_income':exp_income,
                  'exp_income_count':exp_income_count,
                  'inco':inco,
                  'expe':expe,
                  'balans':balans,
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/admin_income_expence.html',content)
    else:
        return redirect('/')
    

def admin_income_expence_add(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------
        
        if request.method =='POST':

            if request.POST['emp_state'] == '0':
                state=None
            else:
                state= Register_State.objects.get(id=int(request.POST['emp_state']))

            ex_in=IncomeExpence()
            ex_in.exin_head_name=request.POST['adexin_head_name'].upper()
            ex_in.exin_date=request.POST['adexin_date']
            ex_in.exin_amount=request.POST['adexin_amt']
            ex_in.exin_dese=request.POST['adexin_dese']
            ex_in.exin_typ=request.POST['adexin_type']
            ex_in.exin_state=state
            ex_in.exin_status=1
            ex_in.save()
            success_msg='Success! Income/Expence recorded.'

            exp_income=IncomeExpence.objects.filter(exin_status=1,).order_by('-exin_date')
            exp_income_count=IncomeExpence.objects.filter(exin_status=1,).count()
    

            content = {'admin_DHB':admin_DHB,
                    'exp_income':exp_income,
                    'success_msg':success_msg,
                    'exp_income_count':exp_income_count
                    }

        else:
            error_msg = 'Opps ! Somethin wrong.'

            exp_income=IncomeExpence.objects.filter(exin_status=1,).order_by('-exin_date')
            exp_income_count=IncomeExpence.objects.filter(exin_status=1,).count()

            content = {'admin_DHB':admin_DHB,
                    'exp_income':exp_income,
                    'error_msg':error_msg,
                    'exp_income_count':exp_income_count
                    }
            
        common_data = nav_data(request)
        # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/admin_income_expence.html',content)
    else:
        return redirect('/')

    

def admin_income_expence_search(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.method == 'POST':
        
            exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=request.POST['admininexfr_data'],exin_date__lte=request.POST['adinexto_date']).order_by('-exin_date')
            inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_date__gte=request.POST['admininexfr_data'],exin_date__lte=request.POST['adinexto_date']).aggregate(intol=Sum('exin_amount'))['intol']
            expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_date__gte=request.POST['admininexfr_data'],exin_date__lte=request.POST['adinexto_date']).aggregate(exptol=Sum('exin_amount'))['exptol']
        
            content={'inco':inco,'expe':expe}
            return render(request,'Admin/admin_income_expence.html',{'exp_income':exp_income,'content':content})
        else:
            return redirect('admin_income_expence')
    
    else:
        return redirect('/')
    


    


def admin_salary_expence(request):
    
   
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------

        # --------------------Current month --------------------
        
        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        # -------------------- End Current month --------------------

        emp_reg_count=EmployeeRegister.objects.filter(emp_status=1).count()
        emp_sal_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).count()
        
        emp_paid=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        emp_unpaid=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_paid.values_list('empreg_id', flat=True)).count()
        emp_unpaid_amt=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_paid.values_list('empreg_id', flat=True)).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']
        emp_sal_acc_deative=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=0,).count()
       
        emp_salary_tol=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empdofj__lt=fr_date).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']
        salary=EmployeeSalary.objects.filter(emp_paidstatus=1)

        if request.method == 'POST':

            sdate= request.POST['start_date']
            edate= request.POST['end_date']

            if request.POST['search_select'] == '0' and sdate and edate:

                salary=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=sdate,empslaray_date__lte=edate)

            elif request.POST['search_select'] and sdate and edate:

                state = Register_State.objects.get(id=int(request.POST['search_select']))
                emp = EmployeeRegister.objects.filter(empstate=state.state_name)
                salary=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=sdate,empslaray_date__lte=edate,empreg_id__in=emp)
            
            elif request.POST['search_select'] !='0':

                state = Register_State.objects.get(id=int(request.POST['search_select']))
                emp = EmployeeRegister.objects.filter(empstate=state.state_name)
                salary=EmployeeSalary.objects.filter(emp_paidstatus=1,empreg_id__in=emp)
            else:
                salary=EmployeeSalary.objects.filter(emp_paidstatus=1)

        salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        
        
        content = {'admin_DHB':admin_DHB,
                    'emp_sal_count':emp_sal_count,
                    'emp_unpaid':emp_unpaid,
                    'emp_sal_acc_deative':emp_sal_acc_deative,
                    'salary':salary,
                    'emp_reg_count':emp_reg_count,
                    'emp_salary_tol':emp_salary_tol,
                    'salary_tol':salary_tol,
                    'emp_unpaid_amt':emp_unpaid_amt
                    }
            
        common_data = nav_data(request)
        # Merge the two dictionaries
        content = {**content, **common_data}
       
        
        return render(request,'Admin/admin_salary_expence.html',content)
    else:
        return redirect('/')
    

def admin_all_salary_expence(request):

     
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
     
        
        salary=EmployeeSalary.objects.filter(emp_paidstatus=1).order_by('empslaray_date')
        salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']
        return render(request,'Admin/admin_all_salary_expence.html',{'salary':salary,'salary_tol':salary_tol})

    else:
        return redirect('/')
    

    
def admin_search_salary_payments(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
           
        if request.method == 'POST':
        
            salary=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=request.POST['adfullfr_data'],empslaray_date__lte=request.POST['adfullpto_date']).order_by('empslaray_date')
            salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=request.POST['adfullfr_data'],empslaray_date__lte=request.POST['adfullpto_date']).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']
            return render(request,'Admin/admin_all_salary_expence.html',{'salary':salary,'salary_tol':salary_tol})

    else:
        return redirect('/')
    

def admin_employee_salary_details(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------
        
        emp_reg_edit=EmployeeRegister.objects.get(id=pk)
        emp_reg=EmployeeRegister.objects.all()
        salary=EmployeeSalary.objects.filter(empreg_id=pk)
        salary_count=EmployeeSalary.objects.filter(empreg_id=pk).count()
        salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empreg_id=pk).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']

        content = {'admin_DHB':admin_DHB,
                    'emp_reg_edit':emp_reg_edit,
                    'salary':salary,
                    'salary_tol':salary_tol,
                    'salary_count':salary_count,
                    'emp_reg':emp_reg
                    }
            
        common_data = nav_data(request)
        # Merge the two dictionaries
        content = {**content, **common_data}
        return render(request,'Admin/admin_employee_salary_details.html',content)
    else:
        return redirect('/')
    

def admin_employee_salary_payments_search(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
         
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        emp_reg=EmployeeRegister.objects.all()
       
        #---------------------------------------------------
        
        if request.method =='POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']

            if request.POST['search_select'] == '0' and sdate and edate:

                emp_reg_edit=EmployeeRegister.objects.get(id=pk)
                salary=EmployeeSalary.objects.filter(empreg_id=pk,empslaray_date__gte=sdate,empslaray_date__lte=edate)
                salary_count=EmployeeSalary.objects.filter(empreg_id=pk,empslaray_date__gte=sdate,empslaray_date__lte=edate).count()
                salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empreg_id=pk,empslaray_date__gte=sdate,empslaray_date__lte=edate).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']

            elif request.POST['search_select'] != '0':

                emp_reg_edit=EmployeeRegister.objects.get(id=int(request.POST['search_select'])) 
                salary=EmployeeSalary.objects.filter(empreg_id=int(request.POST['search_select']))
                salary_count=EmployeeSalary.objects.filter(empreg_id=int(request.POST['search_select'])).count()
                salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empreg_id=int(request.POST['search_select'])).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']
            
            elif request.POST['search_select'] != '0' and sdate and edate:
                emp_reg_edit=EmployeeRegister.objects.get(id=int(request.POST['search_select']))
                salary=EmployeeSalary.objects.filter(empreg_id=int(request.POST['search_select']),empslaray_date__gte=sdate,empslaray_date__lte=edate)
                salary_count=EmployeeSalary.objects.filter(empreg_id=int(request.POST['search_select']),empslaray_date__gte=sdate,empslaray_date__lte=edate).count()
                salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empreg_id=int(request.POST['search_select']),empslaray_date__gte=sdate,empslaray_date__lte=edate).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']
            
            else:
                emp_reg_edit=EmployeeRegister.objects.get(id=pk)
                salary=EmployeeSalary.objects.filter(empreg_id=pk)
                salary_count=EmployeeSalary.objects.filter(empreg_id=pk).count()
                salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empreg_id=pk).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']



        content = {'admin_DHB':admin_DHB,
                    'emp_reg_edit':emp_reg_edit,
                    'salary':salary,
                    'salary_tol':salary_tol,
                    'salary_count':salary_count,
                    'emp_reg':emp_reg
                    }
            
        common_data = nav_data(request)
        # Merge the two dictionaries
        content = {**content, **common_data}
        return render(request,'Admin/admin_employee_salary_details.html',content)
    else:
        return redirect('/')
    

def admin_emp_reg_deactive(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        emp_reg.emp_status=0
        emp_reg.save()
        messages.info(request, emp_reg.empfullName + ' Registration status deactivate')
        return redirect('admin_emp_Register_view')
    else:
        return redirect('/')
    

def admin_emp_reg_reactive(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        emp_reg.emp_status=1
        emp_reg.save()
        messages.info(request, emp_reg.empfullName + ' Registration status activate')
        return redirect('admin_emp_Register_view')
    else:
        return redirect('/')
    

def admin_emp_salary_active(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        emp_reg.emp_salary_status=1
        emp_reg.save()
        messages.info(request, emp_reg.empfullName + ' Salary status activate')
        return redirect('admin_emp_Register_view')
    else:
        return redirect('/')
    

def admin_emp_salary_deactive(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        emp_reg.emp_salary_status=0
        emp_reg.save()
        messages.info(request, emp_reg.empfullName + ' Salary status deactivate')
        return redirect('admin_emp_Register_view')
    else:
        return redirect('/')
    

def admin_emp_reg_delete(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        name=emp_reg.empfullName
        emp_reg.delete()
        messages.info(request, name + ' All Details Permanently')
        return redirect('admin_emp_Register_view')
    else:
        return redirect('/')
    

def admin_fixed_expence(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------
        
    
        fixedexp=FixedExpence.objects.all()
        fixedexp_count=FixedExpence.objects.all().count()

        if request.method=='POST':
            sdate=request.POST['start_date']
            edate=request.POST['end_date']

            if request.POST['search_select'] == '0' and sdate and edate:
                fixedexp=FixedExpence.objects.filter(fixed_date__gte=sdate,fixed_date__lte=edate)
                fixedexp_count=FixedExpence.objects.filter(fixed_date__gte=sdate,fixed_date__lte=edate).count()
            
            elif request.POST['search_select'] and sdate and edate:
                state=Register_State.objects.get(id=int(request.POST['search_select']))
                fixedexp=FixedExpence.objects.filter(fixed_date__gte=sdate,fixed_date__lte=edate,fixed_state=state)
                fixedexp_count=FixedExpence.objects.filter(fixed_date__gte=sdate,fixed_date__lte=edate,fixed_state=state).count()

            elif request.POST['search_select'] !='0':
                state=Register_State.objects.get(id=int(request.POST['search_select']))
                fixedexp=FixedExpence.objects.filter(fixed_state=state)
                fixedexp_count=FixedExpence.objects.filter(fixed_state=state).count()

            else:
                fixedexp=FixedExpence.objects.all()
                fixedexp_count=FixedExpence.objects.all().count()


        content = {'admin_DHB':admin_DHB,
                    'fixedexp':fixedexp,
                    'fixedexp_count':fixedexp_count
                    }
            
        common_data = nav_data(request)

        # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/admin_fixed_expence.html',content)
    else:
        return redirect('/')
 
    
def admin_fixed_expence_add(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------

        if request.method =='POST':


            if request.POST['fixedid']:

                fixedexp_reg=FixedExpence.objects.get(id=int(request.POST['fixedid']))

                fixedexp_reg.fixed_head_name=request.POST['fixed_head_name'].upper()
                fixedexp_reg.fixed_date=request.POST['fixed_date']
                fixedexp_reg.fixed_amount=request.POST['fixed_amt']
                fixedexp_reg.fixed_dese=request.POST['fixed_dese']

                if request.POST['fixed_state'] == '0':
                    fixedexp_reg.fixed_state=fixedexp_reg.fixed_state

                else:
                    state= Register_State.objects.get(id=int(request.POST['fixed_state']))
                    fixedexp_reg.fixed_state=state

                fixedexp_reg.fixed_state=state
                fixedexp_reg.fixed_status=1
                
                fixedexp_reg.save()

                success_msg='Success! Fixed expence Edit.'
                 
                
                    
            
            else:

                if request.POST['fixed_state'] == '0':
                    state=None

                else:
                    state= Register_State.objects.get(id=int(request.POST['fixed_state']))

                fixedexp_reg=FixedExpence()
                fixedexp_reg.fixed_head_name=request.POST['fixed_head_name'].upper()
                fixedexp_reg.fixed_date=request.POST['fixed_date']
                fixedexp_reg.fixed_amount=request.POST['fixed_amt']
                fixedexp_reg.fixed_dese=request.POST['fixed_dese']
                fixedexp_reg.fixed_state=state
                fixedexp_reg.fixed_status=1
                
                fixedexp_reg.save()

                success_msg='Success! Fixed expence added.'
            fixedexp=FixedExpence.objects.all()
            fixedexp_count=FixedExpence.objects.all().count()
        
            content = {'admin_DHB':admin_DHB,
                            'fixedexp':fixedexp,
                            'fixedexp_count':fixedexp_count,
                            'success_msg':success_msg
                            }

     
            
            common_data = nav_data(request)

            # Merge the two dictionaries
            content = {**content, **common_data}
        
            return render(request,'Admin/admin_fixed_expence.html',content)
    else:
        return redirect('/')
    

def admin_fixed_edit(request,pk):
    fixededit=FixedExpence.objects.get(id=pk)
    content = {
       'state_name': fixededit.fixed_state.state_name,
       'head_name': fixededit.fixed_head_name,
       'amount': fixededit.fixed_amount,
       'descr': fixededit.fixed_dese,
       'date': fixededit.fixed_date,
       'edit_id':pk,

    }
    return JsonResponse(content)
    
   
def admin_fixed_change_status(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        fixededit=FixedExpence.objects.get(id=pk)
        if fixededit.fixed_status == 1:
            fixededit.fixed_status=0
        else:
             fixededit.fixed_status=1
        fixededit.save()
        fixedexp=FixedExpence.objects.all()
        content=''
        fixededit=''
        return render(request,'Admin/admin_fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
        
    else:
        return redirect('/')

def admin_fixed_delete(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------
        try:
            fixededit=FixedExpence.objects.get(fixed_status=1,id=pk)
            fixededit.delete()
        except:
            print('No Date')
       
       
        fixedexp=FixedExpence.objects.all()
        fixedexp_count=FixedExpence.objects.all().count()
        
        error_msg='Opps! Data removed'
       
        content = {'admin_DHB':admin_DHB,
                    'fixedexp':fixedexp,
                    'fixedexp_count':fixedexp_count,
                    'error_msg':error_msg
                            }

     
            
        common_data = nav_data(request)

        # Merge the two dictionaries
        content = {**content, **common_data}
        return render(request,'Admin/admin_fixed_expence.html',content)
        
    else:
        return redirect('/')


def admin_company_holoidays(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------
        
        comp_holidays=Company_Holidays.objects.all()
        comp_holidays_count=Company_Holidays.objects.all().count()

        if request.method=='POST':
            sdate=request.POST['start_date']
            edate=request.POST['end_date']

            if request.POST['search_select'] == '0' and sdate and edate :
                comp_holidays=Company_Holidays.objects.filter(ch_sdate__gte=sdate,ch_edate__lte=edate)
                comp_holidays_count=Company_Holidays.objects.filter(ch_sdate__gte=sdate,ch_edate__lte=edate).count()

            elif request.POST['search_select']  and sdate and edate :
                state=Register_State.objects.get(id=int(request.POST['search_select'] ))
                comp_holidays=Company_Holidays.objects.filter(ch_sdate__gte=sdate,ch_edate__lte=edate,ch_state=state)
                comp_holidays_count=Company_Holidays.objects.filter(ch_sdate__gte=sdate,ch_edate__lte=edate,ch_state=state).count()
            
            elif request.POST['search_select'] != '0':
                state=Register_State.objects.get(id=int(request.POST['search_select'] ))
                comp_holidays=Company_Holidays.objects.filter(ch_state=state)
                comp_holidays_count=Company_Holidays.objects.filter(ch_state=state).count()
            
            else:
                comp_holidays=Company_Holidays.objects.all()
                comp_holidays_count=Company_Holidays.objects.all().count()



        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                  'comp_holidays':comp_holidays,
                  'comp_holidays_count':comp_holidays_count
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/admin_company_holidays.html',content)
    else:
        return redirect('/')
    

def admin_company_holiday_add(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
       
        #---------------------------------------------------
        
        if request.method =='POST':
            
            
            if request.POST.get('cmphid'):
                comp_holidays_edit=Company_Holidays.objects.get(id=int(request.POST['cmphid']))
                comp_holidays_edit.ch_sdate=request.POST['cmphsdate']
                comp_holidays_edit.ch_edate=request.POST['cmphedate']
                comp_holidays_edit.ch_no=request.POST['cmphno']

                if request.POST['holiday_state'] == '0':
                    comp_holidays_edit.ch_state= comp_holidays_edit.ch_state
                else:
                    state=Register_State.objects.get(id=int(request.POST['holiday_state']))
                    comp_holidays_edit.ch_state= state

                e = datetime.strptime(request.POST['cmphedate'], '%Y-%m-%d')
                s = datetime.strptime(request.POST['cmphsdate'], '%Y-%m-%d')

                month_days = (e - s).days + 1
                comp_holidays_edit.ch_workno=int(month_days) - int(request.POST['cmphno'])
               
                comp_holidays_edit.save()
                success_msg='Success! Holiday Data Edited.'

            else:

                if request.POST['holiday_state'] == '0':
                    state=None
                else:
                    state=Register_State.objects.get(id=int(request.POST['holiday_state']))
            
                comp_holiday=Company_Holidays()
                comp_holiday.ch_sdate=request.POST['cmphsdate']
                comp_holiday.ch_edate=request.POST['cmphedate']
                comp_holiday.ch_no=request.POST['cmphno']
                comp_holiday.ch_state=state

                #company workdays Calculations
                e = datetime.strptime(request.POST['cmphedate'], '%Y-%m-%d')
                s = datetime.strptime(request.POST['cmphsdate'], '%Y-%m-%d')

                month_days = (e - s).days + 1
                comp_holiday.ch_workno=int(month_days) - int(request.POST['cmphno'])
            
                comp_holiday.save()
                success_msg='Success! Holiday Data added.'

            comp_holidays=Company_Holidays.objects.all()
            comp_holidays_count=Company_Holidays.objects.all().count()

        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                  'comp_holidays':comp_holidays,
                  'comp_holidays_count':comp_holidays_count,
                  'success_msg':success_msg
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}
        return render(request,'Admin/admin_company_holidays.html',content)
    else:
        return redirect('/')


def admin_company_holidy_edit(request,pk):
   
    comp_holidays_edit=Company_Holidays.objects.get(id=pk)
    content = {
       'state_name': comp_holidays_edit.ch_state.state_name,
       'days': comp_holidays_edit.ch_no,
       'sdate': comp_holidays_edit.ch_sdate,
       'edate': comp_holidays_edit.ch_edate,
       'edit_id':pk,

    }
    return JsonResponse(content)
    

# Analysi Section 

def admin_analysis(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)

        # current month 
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 


        
        next_month = cur_date.replace(day=28) + timedelta(days=4)  # get the next month by adding 4 days to the 28th day
        next_month_start = next_month.replace(day=1)  # get the first day of the next month
        next_month_end = next_month_start.replace(day=28) - timedelta(days=1)  # get the last day of the next month by subtracting 1 day from the 28th day
      
        income=IncomeExpence.objects.filter(exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        expence=IncomeExpence.objects.filter(exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
        
        if not income:
            income=1
        if not expence:
            expence=1
        balans=int(income) -int(expence)
        
        bal_p= income - expence 
        if bal_p < 0:
            
            bal_p=-(bal_p)
        
        exp_pr=int(expence) / int(bal_p + income + expence)
        inc_pr=int(income) / int(bal_p + income + expence)
        bal_pr=int(bal_p) / int(bal_p + income + expence)


        # Next Month Income And Expence 
        next_month_income=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        next_month_exp=FixedExpence.objects.filter(fixed_status=1,fixed_date__gte=next_month_start,fixed_date__lte=next_month_end).aggregate(Sum('fixed_amount'))['fixed_amount__sum']

        if not next_month_income:
            next_month_income=0

        if not next_month_exp:
            next_month_exp=1

        next_balans=int(next_month_income) - int(next_month_exp)
        
        
        
        # ========================= income expence section  End =========================


     
        #current monthe income expence calculations
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        income_total=0
        exp_total=0

        income_value = IncomeExpence.objects.filter(exin_date__gte=fr_date,exin_date__lte=to_date,exin_typ=1)
        for i in income_value:
            income_total=income_total+int(i.exin_amount)
       

        expence_value = IncomeExpence.objects.filter(exin_date__gte=fr_date,exin_date__lte=to_date,exin_typ=2)
        for i in expence_value:
            exp_total=exp_total+int(i.exin_amount)
       
        
        bala_value= income_total - exp_total

        if income_total >= exp_total:
            bala_value_chart= income_total - exp_total
            
        else:
            bala_value_chart= exp_total - income_total
           


        #---------------Previous month income and expence -------------------
        # Get the current date

        current_date = datetime.now().date()
        # Calculate the first day of the previous month
        first_day_previous_month = current_date.replace(day=1) - timedelta(days=1)
        previousfr_date = first_day_previous_month.replace(day=1)
      
        
        # Calculate the last day of the month corresponding to first_day_previous_month
        last_day_previous_month = previousfr_date.replace(day=1) + timedelta(days=31)
        preto_date = last_day_previous_month - timedelta(days=1)


        previosincome_total=0
        previosexp_total=0

        income_value = IncomeExpence.objects.filter(exin_date__gte=previousfr_date,exin_date__lte=preto_date,exin_typ=1)
        for i in income_value:
            previosincome_total=previosincome_total+int(i.exin_amount)
       

        expence_value = IncomeExpence.objects.filter(exin_date__gte=previousfr_date,exin_date__lte=preto_date,exin_typ=2)
        for i in expence_value:
            previosexp_total=previosexp_total+int(i.exin_amount)

        prebala_value= previosincome_total - previosexp_total
        # calculating how much increment achieved in current month compare to previous month

        income_precentage= ((income_total - previosincome_total)/previosincome_total)
        expence_precentage= ((exp_total - previosexp_total)/previosexp_total)
        balance_precentage= ((bala_value - prebala_value)/prebala_value)

        # Making the digit to 2 decimal points 
        income_precentage=round(income_precentage, 2)
        expence_precentage=round(expence_precentage, 2)
        balance_precentage=round(balance_precentage, 2)
       
        
       
        #--------------------------------------------------------------------

        common_data = nav_data(request)


        content={
                 'admin_DHB':admin_DHB,
                 'next_month_income':next_month_income,
                 'next_month_exp':next_month_exp,
                 'next_balans':next_balans,
                 'income':income,
                 'expence':expence,
                 'balans':balans,
                 'income_precentage':income_precentage,
                 'expence_precentage':expence_precentage,
                 'balance_precentage':balance_precentage,
                 'previosincome_total':previosincome_total,
                 'previosexp_total':previosexp_total,
                 'prebala_value':prebala_value,
                 'bal_pr':bal_pr,
                 'exp_pr':exp_pr,
                 'cur_date':cur_date,
                 'inc_pr':inc_pr,
                 'income_total':income_total,
                 'exp_total':exp_total,
                 'bala_value':bala_value,
                 'bala_value_chart':bala_value_chart,
                
                }
         # Merge the two dictionaries
        content = {**content, **common_data}

  
        return render(request,'Admin/admin_analysis.html',content)
    
    else:
        return redirect('/')
 

#Createrd for detaild view of Income and Expence 

def admin_analysis_income_expence_details(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')

        admin_DHB=Dashboard_Register.objects.get(id=admid)

        # current month  start date and end date 
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        
        exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('-id')
        exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=fr_date,exin_date__lte=to_date).count()
        inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(intol=Sum('exin_amount'))['intol']
        expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(exptol=Sum('exin_amount'))['exptol']
      

        
        if request.method == 'POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']


            if request.POST['search_select'] == '0' and sdate and edate :
                 
                exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=sdate,exin_date__lte=edate).order_by('-id')
                exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=sdate,exin_date__lte=edate).count()

                inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_date__gte=sdate,exin_date__lte=edate).aggregate(intol=Sum('exin_amount'))['intol']
                expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_date__gte=sdate,exin_date__lte=edate).aggregate(exptol=Sum('exin_amount'))['exptol']
                
                
       
            elif request.POST['search_select'] and sdate and edate :

                state = Register_State.objects.get(id=int(request.POST['search_select']))
                exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=sdate,exin_date__lte=edate,exin_state=state).order_by('-id')
                exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=sdate,exin_date__lte=edate,exin_state=state).count()

                inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_date__gte=sdate,exin_date__lte=edate,exin_state=state).aggregate(intol=Sum('exin_amount'))['intol']
                expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_date__gte=sdate,exin_date__lte=edate,exin_state=state).aggregate(exptol=Sum('exin_amount'))['exptol']
               
            
            elif  request.POST['search_select'] != '0':

                state = Register_State.objects.get(id=int(request.POST['search_select']))
                exp_income=IncomeExpence.objects.filter(exin_status=1,exin_state=state).order_by('-id')
                exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_state=state).count()

                inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1,exin_state=state).aggregate(intol=Sum('exin_amount'))['intol']
                expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2,exin_state=state).aggregate(exptol=Sum('exin_amount'))['exptol']
               
            
            else:
                exp_income=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=fr_date,exin_date__lte=to_date).order_by('-id')
                exp_income_count=IncomeExpence.objects.filter(exin_status=1,exin_date__gte=fr_date,exin_date__lte=to_date).count()

       
        if expe == None:
           expe=0
        if inco == None:
           inco=0

        balans=inco-expe
    

        common_data = nav_data(request)

        content={
                'admin_DHB':admin_DHB,'inco':inco,
                'expe':expe,
                'balans':balans,
                'exp_income':exp_income,
                'exp_income_count':exp_income_count,
                }
        
        # Merge the two dictionaries
        content = {**content, **common_data}

      
        return render(request,'Admin/admin_analysis_income_expence_details.html',content)
        
    else:
        return redirect('/')


def admin_analysis_OJT_details(request):
 
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)

        # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 


        #------------------ Next Month----------------------------

        next_month = cur_date.replace(day=28) + timedelta(days=4)  # get the next month by adding 4 days to the 28th day
        next_month_start = next_month.replace(day=1)  # get the first day of the next month
        next_month_end = next_month_start.replace(day=28) - timedelta(days=1)  # get the last day of the next month by subtracting 1 day from the 28th day
    

        if request.method=='POST':
            
            if request.POST['start_date']:

                start_date = request.POST['start_date'] 
            else:
                start_date = fr_date
            
            if request.POST['end_date']:
                
                end_date = request.POST['end_date'] 
            else:
                end_date = to_date

            if  request.POST['search_select'] == '0':
                new_reg=Register.objects.filter(dofj__gte=start_date,dofj__lte=end_date)
                reg_c=Register.objects.filter(dofj__gte=start_date,dofj__lte=end_date).count()
            else:
                sid=request.POST['search_select']
                state_id = Register_State.objects.get(id=sid)
                reg_c=Register.objects.filter(dofj__gte=start_date,dofj__lte=end_date,reg_state=state_id).count()
                new_reg=Register.objects.filter(dofj__gte=start_date,dofj__lte=end_date,reg_state=state_id)

        else:
            new_reg=Register.objects.filter(dofj__gte=fr_date,dofj__lte=to_date)
            reg_c=Register.objects.filter(dofj__gte=fr_date,dofj__lte=to_date).count()

        # ==============================OJT section Start =============================


        reg=Register.objects.filter(reg_status=1).count()

        #upcoming payments count
        upcoming_payment_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,reg_status=1).count()


        # ==============================End OJT section  =============================
    
        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'new_reg':new_reg,
                   'reg':reg,'reg_c':reg_c,
                   'upcoming_payment_count':upcoming_payment_count
                 }
        
       

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/admin_analysis_OJT.html',content)
    else:
        return redirect('/')
    

def admin_ojt_registration_all_states(request):
    
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)

       
        #-----------------------------------------------
        if request.method=='POST':
            
            if request.POST['start_date'] and request.POST['end_date'] and  request.POST['search_select'] == '0':

                start_date = request.POST['start_date'] 
                end_date = request.POST['end_date'] 
                all_ojt_reg=Register.objects.filter(dofj__gte=start_date,dofj__lte=end_date,reg_status=1)
                all_ojt_reg_count=Register.objects.filter(dofj__gte=start_date,dofj__lte=end_date,reg_status=1).count()

            elif  request.POST['search_select'] == '0'  :
                all_ojt_reg=Register.objects.filter(reg_status=1)
                all_ojt_reg_count=Register.objects.filter(reg_status=1).count()

            elif  request.POST['search_select']:

                sid=request.POST['search_select']
                state_id = Register_State.objects.get(id=sid)
                all_ojt_reg=Register.objects.filter(reg_state=state_id,reg_status=1)
                all_ojt_reg_count=Register.objects.filter(reg_state=state_id,reg_status=1).count()

            elif request.POST['start_date'] and request.POST['end_date'] and  request.POST['search_select']:

                sid=request.POST['search_select']
                start_date = request.POST['start_date'] 
                end_date = request.POST['end_date'] 
                state_id = Register_State.objects.get(id=sid)
                all_ojt_reg=Register.objects.filter(dofj__gte=start_date,dofj__lte=end_date,reg_state=state_id,reg_status=1)
                all_ojt_reg_count=Register.objects.filter(dofj__gte=start_date,dofj__lte=end_date,reg_state=state_id,reg_status=1).count()
           

        else:
            all_ojt_reg=Register.objects.filter(reg_status=1)
            all_ojt_reg_count=Register.objects.filter(reg_status=1).count()


        common_data = nav_data(request)


        content={
                 'admin_DHB':admin_DHB,
                 'all_ojt_reg':all_ojt_reg,
                 'all_ojt_reg_count':all_ojt_reg_count
                }

         # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/admin_ojt_all_registration.html',content)


    else:
        return redirect('/')


def admin_registartion_ojt_payment_details(request,pk):
     if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)

       
        #-----------------------------------------------

        OJT_payments = OJT_payments_details(request,pk)
        common_data = nav_data(request)


        content={
                 'admin_DHB':admin_DHB,
                 
                }

         # Merge the two dictionaries
        content = {**content, **common_data, **OJT_payments}

        return render(request,'Admin/admin_ojt_payments_view.html',content)


def admin_analysis_employee_details(request):
     
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)

        # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 


        #------------------ Next Month----------------------------

        next_month = cur_date.replace(day=28) + timedelta(days=4)  # get the next month by adding 4 days to the 28th day
        next_month_start = next_month.replace(day=1)  # get the first day of the next month
        next_month_end = next_month_start.replace(day=28) - timedelta(days=1)  # get the last day of the next month by subtracting 1 day from the 28th day
    


    # ============================== Employee section Start =============================

        emp_reg_count=EmployeeRegister.objects.all().count()
        emp_reg_current=EmployeeRegister.objects.filter(empdofj__gte=fr_date,empdofj__lte=to_date)
        emp_reg_current_count=EmployeeRegister.objects.filter(empdofj__gte=fr_date,empdofj__lte=to_date).count()
       
        

        emp_sal_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).count()
        
        emp_paid=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        emp_unpaid=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_paid.values_list('empreg_id', flat=True)).count()
        emp_sal_acc_deative=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=0,).count()
       

        # ============================== Employee section End =============================

        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'emp_sal_count':emp_sal_count,
            'emp_reg_count':emp_reg_count,
            'emp_reg_current':emp_reg_current,
            'emp_reg_current_count':emp_reg_current_count,
            'emp_unpaid':emp_unpaid,
           
            'emp_sal_acc_deative':emp_sal_acc_deative
        }

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/admin_analysis_employee.html',content)
    else:
        return redirect('/')
    

def admin_employee_analyis_registration_all_states(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #---------------------------------------------------

        emp_reg = EmployeeRegister.objects.all()
        emp_reg_count = EmployeeRegister.objects.all().count()

        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'emp_reg':emp_reg,
                   'emp_reg_count':emp_reg_count
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/admin_analysis_all_reg_employee.html',content)
    else:
        return redirect('/')


def admin_emp_salary_paid_list(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #---------------------------------------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        if request.method=='POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']
            
            if request.POST['search_select'] == '0' and sdate and edate :

                emp_sal_paid=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=sdate,empslaray_date__lte=edate).order_by('-empslaray_date')
                emp_sal_paid_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=sdate,empslaray_date__lte=edate).count()
                emp_sal_paid_amt=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=sdate,empslaray_date__lte=edate).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']

            elif request.POST['search_select'] and sdate and edate :
                
                stateName=Register_State.objects.get(id=int(request.POST['search_select'])) 
                emp =EmployeeRegister.objects.filter(empstate=stateName.state_name)
                emp_sal_paid=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=sdate,empslaray_date__lte=edate,empreg_id__in=emp).order_by('-empslaray_date')
                emp_sal_paid_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=sdate,empslaray_date__lte=edate,empreg_id__in=emp).count()
                emp_sal_paid_amt=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=sdate,empslaray_date__lte=edate,empreg_id__in=emp).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']

            elif request.POST['search_select'] != '0':

                stateName=Register_State.objects.get(id=int(request.POST['search_select'])) 
                emp =EmployeeRegister.objects.filter(empstate=stateName.state_name)
                emp_sal_paid=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date,empreg_id__in=emp).order_by('-empslaray_date')
                emp_sal_paid_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date,empreg_id__in=emp).count()
                emp_sal_paid_amt=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date,empreg_id__in=emp).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']

            else:
                emp_sal_paid=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).order_by('-empslaray_date')
                emp_sal_paid_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).count()
                emp_sal_paid_amt=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        

        else:
            emp_sal_paid=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).order_by('-empslaray_date')
            emp_sal_paid_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).count()
            emp_sal_paid_amt=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        
        
        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'emp_sal_paid':emp_sal_paid,
                   'emp_sal_paid_count':emp_sal_paid_count,
                   'emp_sal_paid_amt':emp_sal_paid_amt
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/admin_analysis_employee_salary_paid.html',content)
    else:
        return redirect('/')



def admin_emp_salary_unpaid_list(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #---------------------------------------------------

        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        emp_unp=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        emp_unpaid=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True))
        emp_unpaid_count=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).count()
        emp_unp_amt=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']

        if request.method=='POST':

            sdate=request.POST['start_date']
            edate=request.POST['end_date']

            if request.POST['search_select'] == '0' and sdate and edate :

                emp_unp=EmployeeSalary.objects.filter(empslaray_date__gte=sdate,empslaray_date__lte=edate,emp_paidstatus=1)
                emp_unpaid=EmployeeRegister.objects.filter(empdofj__lt=sdate,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True))
                emp_unpaid_count=EmployeeRegister.objects.filter(empdofj__lt=sdate,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).count()
                emp_unp_amt=EmployeeRegister.objects.filter(empdofj__lt=sdate,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']
            
            elif request.POST['search_select'] and sdate and edate:

                stateName=Register_State.objects.get(id=int(request.POST['search_select'])) 
                emp_unp=EmployeeSalary.objects.filter(empslaray_date__gte=sdate,empslaray_date__lte=to_date,emp_paidstatus=1)

                emp_unpaid=EmployeeRegister.objects.filter(empdofj__lt=sdate,emp_status=1,emp_salary_status=1,empstate=stateName.state_name).exclude(id__in=emp_unp.values_list('empreg_id', flat=True))
                emp_unpaid_count=EmployeeRegister.objects.filter(empdofj__lt=sdate,emp_status=1,emp_salary_status=1,empstate=stateName.state_name).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).count()
                emp_unp_amt=EmployeeRegister.objects.filter(empdofj__lt=sdate,emp_status=1,emp_salary_status=1,empstate=stateName.state_name).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']
            
            
            elif request.POST['search_select'] != '0':

                stateName=Register_State.objects.get(id=int(request.POST['search_select'])) 
                emp_unp=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1)

                emp_unpaid=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empstate=stateName.state_name).exclude(id__in=emp_unp.values_list('empreg_id', flat=True))
                emp_unpaid_count=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empstate=stateName.state_name).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).count()
                emp_unp_amt=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empstate=stateName.state_name).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']

            else:
                emp_unp=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
                emp_unpaid=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True))
                emp_unpaid_count=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).count()
                emp_unp_amt=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']


           

        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'emp_unpaid':emp_unpaid,
                   'emp_unpaid_count':emp_unpaid_count,
                   'emp_unp_amt':emp_unp_amt
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/admin_analysis_employee_unpaid_salary.html',content)
    else:
        return redirect('/')

def admin_emp_deactive_salary_account_list(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #---------------------------------------------------

        if request.method=='POST':

            if request.POST['search_select'] == '0':
                emp_deactive = EmployeeRegister.objects.filter(emp_salary_status=0)
                emp_deactive_count = EmployeeRegister.objects.filter(emp_salary_status=0).count()
            else:
                stateName = Register_State.objects.get(id= int(request.POST['search_select']))
                emp_deactive = EmployeeRegister.objects.filter(emp_salary_status=0,empstate=stateName.state_name)
                emp_deactive_count = EmployeeRegister.objects.filter(emp_salary_status=0).count()
        
        else:

            emp_deactive = EmployeeRegister.objects.filter(emp_salary_status=0)
            emp_deactive_count = EmployeeRegister.objects.filter(emp_salary_status=0).count()

        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'emp_deactive':emp_deactive,
                   'emp_deactive_count':emp_deactive_count,
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/admin_analysis_employee_deactive_salary_account.html',content)
    else:
        return redirect('/')


def admin_emp_salary_pay_details(request,emp_id):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)
        #---------------------------------------------------

        employee = EmployeeRegister.objects.get(id=emp_id)
        emp_salary = EmployeeSalary.objects.filter(empreg_id=employee)

        stateName = Register_State.objects.get(state_name=employee.empstate)


        common_data = nav_data(request)

        content = {'admin_DHB':admin_DHB,
                   'employee':employee,
                   'emp_salary':emp_salary,
                   'stateName':stateName
                   }

        # Merge the two dictionaries
        content = {**content, **common_data}


        return render(request,'Admin/admin_employee_details_payments.html',content)
    else:
        return redirect('/')



def admin_ojt_current_upcoming_payments(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)

        if request.method=='POST':

            if request.POST['search_select'] == '0':
                
                up_payments = upcoming_payments(request)
            
            else:
                state_id=Register_State.objects.get(id=int(request.POST['search_select']))
                up_payments = upcoming_state_payments(request,state_id)   
        
        else:

            up_payments = upcoming_payments(request)


        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB}
            # Merge the two dictionaries
        content = {**content, **common_data, **up_payments}

        return render(request,'Admin/admin_ojt_upcoming_payments.html',content)
    else:
        return redirect('/')


def admin_ojt_analysis_payment_status(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        admin_DHB = Dashboard_Register.objects.get(id=admid)

        if request.method=='POST':
            if request.POST['search_select'] == '0':

                all_pending_reg = Register.objects.all()
                all_pending_reg_count = Register.objects.all().count()

                pending_reg=Register.objects.filter(payment_status=0)
                pending_reg_count=Register.objects.filter(payment_status=0).count()
                pending_amt=Register.objects.filter(payment_status=0).aggregate(Sum('regbalance_amt'))

                complete_reg=Register.objects.filter(payment_status=1)
                complete_regcount=Register.objects.filter(payment_status=1).count()
                complete_reg_amt=Register.objects.filter(payment_status=1).aggregate(Sum('regtotal_amt'))

                incomplete_reg=Register.objects.filter(payment_status=2)
                incomplete_reg_count=Register.objects.filter(payment_status=2).count()
                incomplete_reg_amt=Register.objects.filter(payment_status=2).aggregate(Sum('regtotal_amt'))


            else:

                state_id=Register_State.objects.get(id=int(request.POST['search_select']))

                all_pending_reg = Register.objects.filter(reg_state=state_id)
                all_pending_reg_count = Register.objects.filter(reg_state=state_id).count()

                #pending payment
                pending_reg=Register.objects.filter(payment_status=0,reg_state=state_id)
                pending_reg_count=Register.objects.filter(payment_status=0).count()
                pending_amt=Register.objects.filter(payment_status=0,reg_state=state_id).aggregate(Sum('regbalance_amt'))

                complete_reg=Register.objects.filter(payment_status=1,reg_state=state_id)
                complete_regcount=Register.objects.filter(payment_status=1,reg_state=state_id).count()
                complete_reg_amt=Register.objects.filter(payment_status=1,reg_state=state_id).aggregate(Sum('regtotal_amt'))

                incomplete_reg=Register.objects.filter(payment_status=2,reg_state=state_id)
                incomplete_reg_count=Register.objects.filter(payment_status=2,reg_state=state_id).count()
                incomplete_reg_amt=Register.objects.filter(payment_status=2,reg_state=state_id).aggregate(Sum('regtotal_amt'))
        else:
        
            all_pending_reg = Register.objects.all()
            all_pending_reg_count = Register.objects.all().count()

            pending_reg=Register.objects.filter(payment_status=0)
            pending_reg_count=Register.objects.filter(payment_status=0).count()
            pending_amt=Register.objects.filter(payment_status=0).aggregate(Sum('regbalance_amt'))

            complete_reg=Register.objects.filter(payment_status=1)
            complete_regcount=Register.objects.filter(payment_status=1).count()
            complete_reg_amt=Register.objects.filter(payment_status=1).aggregate(Sum('regtotal_amt'))

            incomplete_reg=Register.objects.filter(payment_status=2)
            incomplete_reg_count=Register.objects.filter(payment_status=2).count()
            incomplete_reg_amt=Register.objects.filter(payment_status=2).aggregate(Sum('regtotal_amt'))

        common_data = nav_data(request)

        content={'admin_DHB':admin_DHB,
                 'all_pending_reg':all_pending_reg,
                 'all_pending_reg_count':all_pending_reg_count,
                 'pending_reg':pending_reg,
                 'pending_reg_count':pending_reg_count,
                 'pending_amt':pending_amt,
                 'complete_reg':complete_reg,
                 'complete_reg_amt':complete_reg_amt,
                 'complete_regcount':complete_regcount,
                 'incomplete_reg':incomplete_reg,
                 'incomplete_reg_count':incomplete_reg_count,
                 'incomplete_reg_amt':incomplete_reg_amt
                 }
            # Merge the two dictionaries
        content = {**content, **common_data}

        return render(request,'Admin/admin_ojt_analysis_payments_status.html',content)
    else:
        return redirect('/')


def admin_analysis_months(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        current_year = datetime.now().year

        content={
            'months':months,'years':years,'current_year':current_year,}
        return render(request,'Admin/admin_analysis_on_months.html',{'content':content})
    else:
        return redirect('/')
    

def admin_analysis_search(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        current_year = datetime.now().year
        cur_date=datetime.now().date()


        if request.method == 'POST':

            check_month=int(request.POST['admin_ana_month'])
            check_year=int(request.POST['admin_ana_year'])
            month_name = calendar.month_name[check_month]

            # Finding the start date and end date of searched month

            d = datetime(check_year, check_month, 1)
            fr_date = d.replace(day=1).date()
            _, num_days =calendar.monthrange(check_year, check_month)
            to_date = d.replace(day=num_days).date()


            income=IncomeExpence.objects.filter(exin_typ=1,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']
            expence=IncomeExpence.objects.filter(exin_typ=2,exin_date__gte=fr_date,exin_date__lte=to_date).aggregate(Sum('exin_amount'))['exin_amount__sum']

            
            if not income:
                income=1
            if not expence:
                expence=1

            if cur_date < fr_date:

                # Next Month Income And Expence 
                next_month_income=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=fr_date,next_pay_date__lte=to_date).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
                next_month_exp=FixedExpence.objects.filter(fixed_status=1,fixed_date__gte=fr_date,fixed_date__lte=to_date).aggregate(Sum('fixed_amount'))['fixed_amount__sum']
                print(next_month_exp)

                if next_month_income:
                   income = int(income) + int(next_month_income)
                if next_month_exp:
                   expence = int(expence) + int(next_month_exp)


            balans=int(income) -int(expence)
            
            bal_p= income - expence 
            if bal_p < 0:
                
                bal_p=-(bal_p)
            
            exp_pr=int(expence) / int(bal_p + income + expence)
            inc_pr=int(income) / int(bal_p + income + expence)
            bal_pr=int(bal_p) / int(bal_p + income + expence)


            # OJT details Section 
            
            reg_c=Register.objects.filter(dofj__gte=fr_date,dofj__lte=to_date).count()
            reg_c_amt=Register.objects.filter(dofj__gte=fr_date,dofj__lte=to_date,).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']

            # OJT payments  

            after_6_days = fr_date + timedelta(days=6)  
            after_8_days = fr_date + timedelta(days=7)  
            after_15days = fr_date + timedelta(days=14) 

            payhistory1=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
            payhistory8=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
            payhistory15=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
            payhistory1_c=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,).count()
            payhistory8_c=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,).count()
            payhistory15_c=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,).count()


            # Employeee Registraion an salary section

            emp_reg=EmployeeRegister.objects.filter(empdofj__gte=fr_date,empdofj__lte=to_date).count()
            emp_con_sal_amt=EmployeeRegister.objects.filter(empdofj__lt=fr_date,).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']

            emp_sal_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).count()
            emp_sal=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        
            # Salary Payments 

            after_14_days = fr_date + timedelta(days=14)  
            after_15_days = fr_date + timedelta(days=15)  
        

            empsalc_1to7=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=after_14_days,emp_paidstatus=1).count()
            empsal_1to7=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=after_14_days,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
            empsalc_15to=EmployeeSalary.objects.filter(empslaray_date__gte=after_15_days,empslaray_date__lte=to_date,emp_paidstatus=1).count()
            empsal_15to=EmployeeSalary.objects.filter(empslaray_date__gte=after_15_days,empslaray_date__lte=to_date,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']

        else:
            return redirect('admin_analysis_search')
      


        content={
            'month_name':month_name,'months':months,'years':years,'current_year':current_year,'fr_date':fr_date,'to_date':to_date,
            'income':income,'expence':expence,'balans':balans,'exp_pr':exp_pr,'inc_pr':inc_pr,'bal_pr':bal_pr,
            'reg_c':reg_c,'reg_c_amt':reg_c_amt,
            'payhistory1':payhistory1,'payhistory8':payhistory8,'payhistory15':payhistory15,'payhistory1_c':payhistory1_c,'payhistory8_c':payhistory8_c,'payhistory15_c':payhistory15_c,
            'emp_reg':emp_reg,'emp_con_sal_amt':emp_con_sal_amt,'emp_sal_count':emp_sal_count,'emp_sal':emp_sal,
            'empsalc_1to7':empsalc_1to7,'empsal_1to7':empsal_1to7,'empsalc_15to':empsalc_15to,'empsal_15to':empsal_15to,
            }
        return render(request,'Admin/admin_analysis_on_months.html',{'content':content})
        
    else:
        return redirect('/')



def admin_employee_register_form(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        depart=Department.objects.all()
        reg_emps= EmployeeRegister.objects.all().order_by('-id')
        reg_emps_count= EmployeeRegister.objects.count()
        states= Register_State.objects.all()
        content={'depart':depart,'reg_emps':reg_emps,'reg_emps_count':reg_emps_count,'states':states}
        return render(request,'Admin/admin_employee_register_form.html',content)
    else:
        return redirect('/')
    

def admin_employee_register(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        depart=Department.objects.all()

        if request.method == 'POST':
            emp_reg = EmployeeRegister()

            emp_reg.empidreg = request.POST['emp_id']
            emp_reg.empfullName = request.POST['emp_Name']
            emp_reg.empdept_id =Department.objects.get(id=int(request.POST['emp_dept']))
            emp_reg.empdesignation = request.POST['emp_desig']
            emp_reg.empdofj = request.POST['emp_dfj']
            emp_reg.empstate = request.POST['emp_state']

            if request.POST['emp_sal']:

                emp_reg.empconfirmsalary = request.POST['emp_sal']
            else:
                 emp_reg.empconfirmsalary=0
            emp_reg.emp_status = 1
           
            emp_reg.save()

            success_msg= 'Success! New employee data has been saved'
            reg_emps= EmployeeRegister.objects.all().order_by('-id')
            reg_emps_count= EmployeeRegister.objects.count()

            content={'depart':depart,'reg_emps':reg_emps,
                     'reg_emps_count':reg_emps_count,
                     'success_msg':success_msg}
        
        else:

            error_msg= 'Opps! Something went wrong'
            reg_emps= EmployeeRegister.objects.all().order_by('-id')
            reg_emps_count= EmployeeRegister.objects.count()

            content={'depart':depart,'reg_emps':reg_emps,
                     'reg_emps_count':reg_emps_count,
                     'error_msg':error_msg}
            
        return render(request,'Admin/admin_employee_register_form.html',content)

        
    else:
        return redirect('/')



# =========================== End Admin Module Section ======================================


# LogOut Section

def logout_page(request):
    logout(request)
    return redirect('login_page')
        

# Receipt Download single data
def singeldata_receipt(request,pk):

    date = datetime.now().date()   
    payhis = PaymentHistory.objects.get(id=pk)
    r_data=Receipt_Data.objects.first()
    number_in_words = num2words(payhis.payintial_amt)
    template_path = 'account/singledata_Receipt.html'
    context = {'payhis': payhis,
               'r_data':r_data,
               'number_in_words':number_in_words,
    'path':settings.NEWPATH,
    'date':date,
    }
   
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Receipt.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    
     # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



# Receipt Download single user full payment data
def singelUserfull_receipt(request,pk):

    date = datetime.now().date() 
    reg=Register.objects.get(id=pk)  
    payhis = PaymentHistory.objects.filter(reg_id=reg).last()
    r_data=Receipt_Data.objects.first()
    number_in_words = num2words(reg.reg_payedtotal)
    template_path = 'account/singleUser_full_Receipt.html'
    context = {'reg': reg,
               'payhis':payhis,
               'r_data':r_data,
               'number_in_words':number_in_words,
     'path':settings.NEWPATH,
    'date':date,
    }
   
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Full-Receipt.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    
     # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

