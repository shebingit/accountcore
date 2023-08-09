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
from xhtml2pdf import pisa
from num2words import num2words
import calendar
from django.db.models import Sum
from django.core.mail import send_mail
from django.db.models import Q


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

def account_password_change(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
           
        else:
            return redirect('/')
        
        if request.method=='POST':
            username=request.POST['urname']
            password=request.POST['pws']

            user=User.objects.get(id=uid)
            if username:
                user.username=username
            else:
                user.username= user.username
            user.set_password(password)
            user.save()
            msg=1
        return render(request,'account/account_profile.html',{'user':user,'msg':msg})

    else:
        return redirect('/')
    




#login Authentication
def login_dashboard(request):
    if request.method=='POST':
            username=request.POST['uname']
            password=request.POST['psw']
            user=authenticate(username=username,password=password)
        
            
            if user is not None:
                if user.is_superuser == 1:
                    request.session["admid"]=user.id
                    login(request, user)
                    if 'admid' in request.session:
                        if request.session.has_key('admid'):
                            admid = request.session['admid']
                        else:
                            return redirect('/')
                        
                        cur_date=datetime.now().date()
                        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
                        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
                        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

                        #Income adding to IncomeExpence Table
                        if PaymentHistory.objects.exists():
                            inexpe=IncomeExpence.objects.filter(exin_head_name='OJT',exin_date__gte=fr_date,exin_date__lte=to_date).first()
                            payhis=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
                            #payhi_last=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).last()

                            if payhis:

                                if inexpe:
                                    inexpe.exin_head_name='OJT'
                                    inexpe.exin_amount=payhis
                                    inexpe.exin_typ=1
                                    inexpe.exin_date=to_date
                                    inexpe.exin_status=1
                                    inexpe.save()

                                else:

                                    incexpence=IncomeExpence()
                                    incexpence.exin_head_name='OJT'
                                    incexpence.exin_amount=payhis
                                    incexpence.exin_typ=1
                                    incexpence.exin_date=cur_date
                                    incexpence.exin_status=1
                                    incexpence.save()
                            else:
                                print('Payment History Is Amount Empty')
                        else:
                            print('Payment History Is Empty')

                        # Salay Expence adding to IncomeExpence Table

                        if EmployeeSalary.objects.exists():

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
                                print('Employee Salary Is Amount Empty')
                        else:
                            print('Employee Salary Is Empty')

                        # Fixed Expence adding to the IncomeEpence Table

                        fixexp=FixedExpence.objects.filter(fixed_date__lte=cur_date,fixed_date__gte=fr_date,fixed_status=1)
                        
                        inex = IncomeExpence.objects.filter(exin_date__in=fixexp.values_list('fixed_date', flat=True)).filter(exin_head_name__in=fixexp.values_list('fixed_head_name', flat=True))
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

                        


                        reg=Register.objects.filter(reg_status=0)
                        payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg).count
                        reg1=Register.objects.filter(reg_status=1)
                        payhis_list=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1)
                        msg_succes=1
                        return render(request,'Admin/Admin_dashboard.html',{'payhis':payhis,'payhis_list':payhis_list,'msg_succes':msg_succes})
                    
                    else:
                        return redirect('/')
                    
                
                else:
                    request.session["uid"]=user.id
                    login(request, user)

                    if request.session.has_key('uid'):
                        uid = request.session['uid']
                        reg=Register.objects.filter(reg_status=1)
                        reg_count=Register.objects.all().count()
                        dept_count=Department.objects.all().count()

                        cur_date=datetime.now().date()
                        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
                        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
                        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

                        #Income adding to IncomeExpence Table
                        if PaymentHistory.objects.exists():
                            inexpe=IncomeExpence.objects.filter(exin_head_name='OJT',exin_date__gte=fr_date,exin_date__lte=to_date).first()
                            payhis=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
                            #payhi_last=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).last()

                            if payhis:

                                if inexpe:
                                    inexpe.exin_head_name='OJT'
                                    inexpe.exin_amount=payhis
                                    inexpe.exin_typ=1
                                    inexpe.exin_date=to_date
                                    inexpe.exin_status=1
                                    inexpe.save()

                                else:

                                    incexpence=IncomeExpence()
                                    incexpence.exin_head_name='OJT'
                                    incexpence.exin_amount=payhis
                                    incexpence.exin_typ=1
                                    incexpence.exin_date=cur_date
                                    incexpence.exin_status=1
                                    incexpence.save()
                            else:
                                print('Payment History Is Amount Empty')
                        else:
                            print('Payment History Is Empty')

                        # Salay Expence adding to IncomeExpence Table

                        if EmployeeSalary.objects.exists():

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
                                print('Employee Salary Is Amount Empty')
                        else:
                            print('Employee Salary Is Empty')

                        # Fixed Expence adding to the IncomeEpence Table

                        fixexp=FixedExpence.objects.filter(fixed_date__lte=cur_date,fixed_date__gte=fr_date,fixed_status=1)
                        
                        inex = IncomeExpence.objects.filter(exin_date__in=fixexp.values_list('fixed_date', flat=True)).filter(exin_head_name__in=fixexp.values_list('fixed_head_name', flat=True))
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

                          
                       
                        pay_pending_count=PaymentHistory.objects.filter(admin_payconfirm=0).count()
                    
                        pay_count=Register.objects.filter(next_pay_date__lte=cur_date).count()
                        msg_succes=1
                        content={'dept_count':dept_count,
                                'reg_count':reg_count,
                                'pay_count':pay_count,
                                'pay_pending_count':pay_pending_count,'msg_succes':msg_succes}
                     
                        return render(request,'account/dashboard.html',{'reg':reg,'cur_date':cur_date,'content':content})
                    
                    else:
                        return redirect('/')
                    
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
        reg=Register.objects.filter(reg_status=1)
        reg_count=Register.objects.all().count()
        dept_count=Department.objects.all().count()

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        #Income adding to IncomeExpence Table
        if PaymentHistory.objects.exists():
            try:
                inexpe=IncomeExpence.objects.filter(exin_head_name='OJT',exin_date__gte=fr_date,exin_date__lte=to_date).first()
                payhis=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
                #payhi_last=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1).last()
                
                if payhis:
                                
                    if inexpe:
                        inexpe.exin_head_name='OJT'
                        inexpe.exin_amount=payhis
                        inexpe.exin_typ=1
                        inexpe.exin_date=to_date
                        inexpe.exin_status=1
                        inexpe.save()

                    else:

                        incexpence=IncomeExpence()
                        incexpence.exin_head_name='OJT'
                        incexpence.exin_amount=payhis
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

        fixexp=FixedExpence.objects.filter(fixed_date__lte=cur_date,fixed_date__gte=fr_date,fixed_status=1)
                        
        inex = IncomeExpence.objects.filter(exin_date__in=fixexp.values_list('fixed_date', flat=True)).filter(exin_head_name__in=fixexp.values_list('fixed_head_name', flat=True))
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



        pay_pending_count=PaymentHistory.objects.filter(admin_payconfirm=0).count()
    
        pay_count=Register.objects.filter(next_pay_date__lte=cur_date).count()
        content={'dept_count':dept_count,
                'reg_count':reg_count,
                'pay_count':pay_count,
                'pay_pending_count':pay_pending_count}
        return render(request,'account/dashboard.html',{'reg':reg,'cur_date':cur_date,'content':content})
    
    else:
        return redirect('/')



def track_payments(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        reg=Register.objects.filter(reg_status=1,payment_status=0)
        cur_date=datetime.now().date()
        return render(request,'account/track_Payments.html',{'reg':reg,'cur_date':cur_date})
    
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


def department_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        dept=Department.objects.all()
        return render(request,'account/Department_form.html',{'dept':dept})
       
    else:
        return redirect('/')


def department_add(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        if request.method =='POST':
            
            if request.POST['dept_id']:
                dept=Department.objects.get(id=int( request.POST['dept_id']))
                dept.department=request.POST['dept_name'].upper()
                dept.save()
                msg=3
            else:
                dept=Department()
                dept.department=request.POST['dept_name'].upper()
                dept.dpt_Status=1
                dept.save()
                msg=1
            dept=Department.objects.all()
            return render(request,'account/Department_form.html',{'msg':msg,'dept':dept})
        else:
            return redirect('department_form')
        
    else:
        return redirect('/')   
    
def edit_dept(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        dept_edit=Department.objects.get(id=pk)

        dept=Department.objects.all()
        return render(request,'account/Department_form.html',{'dept_edit':dept_edit,'dept':dept})
    
    else:
        return redirect('/')
    

    
def remove_dept(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        dept=Department.objects.get(id=pk)
        dept.delete()
        msg=2
        dept=Department.objects.all()
        return render(request,'account/Department_form.html',{'msg':msg,'dept':dept})
    
    else:
        return redirect('/')
    
    
def pyment_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        reg=Register.objects.filter(reg_status=1)
        return render(request,'account/Payment_form.html',{'reg':reg})
    
    else:
        return redirect('/')



def addpayment_details(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        reg_dt=Register.objects.get(id=pk)
        reg=Register.objects.filter(reg_status=1)
        return render(request,'account/Payment_form.html',{'reg':reg,'reg_dt':reg_dt})
    else:
            return redirect('/')



def save_payment(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        if request.method =='POST':

            paymt=PaymentHistory()
            reg=Register.objects.get(id=int(request.POST['payname']))
            pay_amt=int(request.POST['pinit_amunt'])
            total_amt=int(reg.regtotal_amt)
            cal=int(total_amt / 3)

            paymt.reg_id=reg
            paymt.head_name=request.POST['payhname']
            paymt.payintial_amt=pay_amt

            next_date=request.POST['pnxtpdof']
            if next_date:
                reg.next_pay_date=request.POST['pnxtpdof']

            else:
                # Calculate the date after 30 days
            
                current_date = reg.next_pay_date

                if pay_amt >= int(reg.fixed_intial_amt):
                
                    after_days = current_date + timedelta(days=30)
                else:
                    after_days = current_date + timedelta(days=15)

                reg.next_pay_date=after_days

        
            paymt.paydofj=request.POST['pdfj']
            pay_amt=int(request.POST['pinit_amunt'])
            paymt.paybalance_amt=int(reg.regbalance_amt) - pay_amt
            paymt.paytotal_amt=int(reg.reg_payedtotal)
            paymt.save()
            #reg.payprogress=int(request.POST['progres'])
            reg.save()
            msg=1
            reg=Register.objects.filter(reg_status=1)
            return render(request,'account/Payment_form.html',{'reg':reg,'msg':msg})
        
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
    
    
def payhis_remove(request,pk):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
          
        else:
            return redirect('/')
        
        payhis=PaymentHistory.objects.get(id=pk)

        if payhis.admin_payconfirm == 0:
            payhis.delete()

        return redirect('pyment_form')
    
    else:
        return redirect('/')
        
     

def Register_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        dept=Department.objects.filter(dpt_Status=1)
        reg=Register.objects.filter(reg_status=0)
        payhis=PaymentHistory.objects.all()
        return render(request,'account/Register_form.html',{'dept':dept,'reg':reg,'payhis':payhis})
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

def register_edit(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        reg=Register.objects.get(id=pk)
        payhis=PaymentHistory.objects.get(reg_id_id=reg)
        dept=Department.objects.all()
        payhist=PaymentHistory.objects.all()
        if payhis.admin_payconfirm == 0:
            return render(request,'account/register_edit_form.html',{'reg':reg,'dept':dept,'payhist':payhist})
        else:
            return redirect('Register_form')
    else:
        return redirect('/')
    

def register_edit_save(request,pk):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            reg=Register.objects.get(id=pk)
            reg.fullName=request.POST['name']
            reg.Phone=request.POST['phno']
        
            if request.POST['dfj']:
                reg.dofj=request.POST['dfj']
            else:
                reg.dofj=reg.dofj

            reg.refrence=request.POST['refby']
            reg.fixed_intial_amt=int(request.POST['fixedinit_amunt'])
            reg.regtotal_amt=int(request.POST['tot_amount'])
            reg.dept_id=Department.objects.get(id=request.POST['dept'])

            if request.POST['nxtpdof']:
                reg.next_pay_date=request.POST['nxtpdof']
            else:
                reg.next_pay_date= reg.next_pay_date

            payhis=PaymentHistory.objects.get(id=reg.firstpay_id)
            payhis.payintial_amt=request.POST['init_amunt']
            if request.POST['dfpayment']:
                payhis.paydofj=request.POST['dfpayment']
            else:
                payhis.paydofj= payhis.paydofj
            payhis.paytotal_amt= int(request.POST['tot_amount'])  
            payhis.save()
            reg.save()
            return redirect('Register_form')
        else:
            return redirect('Register_form')
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


def remove(request,pk):
        
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        reg=Register.objects.get(id=pk)
        reg.delete()
        dept=Department.objects.filter(dpt_Status=1)
        reg=Register.objects.filter(reg_status=0)
        payhis=PaymentHistory.objects.all()
        msg=3
        return render(request,'account/Register_form.html',{'msg':msg,'dept':dept,'reg':reg,'payhis':payhis})
    
    else:
        return redirect('/')
        


#Payments History section 

def pyments_history(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        reg=Register.objects.filter(reg_status=1)
        payhis=PaymentHistory.objects.all()
        return render(request,'account/payments_history.html',{'reg':reg,'payhis':payhis})
    
    else:
        return redirect('/')

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


#Single User Payments Viev

def singleuser_details(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        reg=Register.objects.get(reg_status=1,id=pk)
        payhis=PaymentHistory.objects.filter(reg_id_id=reg.id)
        return render(request,'account/SingleUser_payments.html',{'reg':reg,'payhis':payhis})
    
    else:
        return redirect('/')    


def reactivate_user(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        reg=Register.objects.get(reg_status=1,id=pk)
        reg.payment_status=0
        reg.save()
        msgalert=reg.fullName + " User is Reactivated"

        reg=Register.objects.filter(reg_status=1)
        reg_count=Register.objects.all().count()
        dept_count=Department.objects.all().count()
        cur_date=datetime.now().date()
        
        pay_pending_count=PaymentHistory.objects.filter(admin_payconfirm=0).count()
    
        pay_count=Register.objects.filter(next_pay_date__lte=cur_date).count()
        content={'dept_count':dept_count,
                'reg_count':reg_count,
                'pay_count':pay_count,
                'pay_pending_count':pay_pending_count}
        return render(request,'account/dashboard.html',{'reg':reg,'cur_date':cur_date,'content':content,'msgalert':msgalert})
    else:
        return redirect('/')
    

def deactive_user(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        reg=Register.objects.get(reg_status=1,id=pk)
        reg.payment_status=2
        reg.save()
        msgalert=reg.fullName + " User is Deactivated"
        reg=Register.objects.filter(reg_status=1)
        reg_count=Register.objects.all().count()
        dept_count=Department.objects.all().count()
        cur_date=datetime.now().date()
        
        pay_pending_count=PaymentHistory.objects.filter(admin_payconfirm=0).count()
    
        pay_count=Register.objects.filter(next_pay_date__lte=cur_date).count()
        content={'dept_count':dept_count,
                'reg_count':reg_count,
                'pay_count':pay_count,
                'pay_pending_count':pay_pending_count}
        return render(request,'account/dashboard.html',{'reg':reg,'cur_date':cur_date,'content':content,'msgalert':msgalert})
    else:
        return redirect('/')

    
def delete_user(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        reg=Register.objects.get(reg_status=1,id=pk)
        reg.payment_status=2
        reg.reg_status=2
        reg.save()
        msgalert=reg.fullname + " User is Deleted"
        reg=Register.objects.filter(reg_status=1)
        reg_count=Register.objects.all().count()
        dept_count=Department.objects.all().count()
        cur_date=datetime.now().date()
        
        pay_pending_count=PaymentHistory.objects.filter(admin_payconfirm=0).count()
    
        pay_count=Register.objects.filter(next_pay_date__lte=cur_date).count()
        content={'dept_count':dept_count,
                'reg_count':reg_count,
                'pay_count':pay_count,
                'pay_pending_count':pay_pending_count}
        return render(request,'account/dashboard.html',{'reg':reg,'cur_date':cur_date,'content':content,'msgalert':msgalert})
    else:
        return redirect('/')


def previous_data(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        try:
            pk=int(pk-1)
            reg=Register.objects.get(reg_status=1,id=pk)
            payhis=PaymentHistory.objects.filter(reg_id_id=reg.id)
            return render(request,'account/SingleUser_payments.html',{'reg':reg,'payhis':payhis})
        
        except Register.DoesNotExist:
            reg=Register.objects.filter(reg_status=1).first()
            payhis=PaymentHistory.objects.filter(reg_id_id=reg.id)
            return render(request,'account/SingleUser_payments.html',{'reg':reg,'payhis':payhis})
    else:
        return redirect('/')
        
    

def next_data(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        try:
            pk=int(pk+1)
            reg=Register.objects.get(reg_status=1,id=pk)
            payhis=PaymentHistory.objects.filter(reg_id_id=reg.id)
            return render(request,'account/SingleUser_payments.html',{'reg':reg,'payhis':payhis})
        except Register.DoesNotExist:
            reg=Register.objects.filter(reg_status=1).last()
            payhis=PaymentHistory.objects.filter(reg_id_id=reg.id)
            return render(request,'account/SingleUser_payments.html',{'reg':reg,'payhis':payhis})
    else:
        return redirect('/')

#   Account Section 

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
    
def fixed_expence(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        fixededit=FixedExpence.objects.all()

        if fixededit:

            fixededit=None   

        fixedexp=FixedExpence.objects.all()
        content=''
        return render(request,'account/fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
    else:
        return redirect('/')


def fixed_expence_add(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.POST['fixed_id']:

            fixededit=FixedExpence.objects.get(fixed_status=1,id=int(request.POST['fixed_id']))
            fixededit.fixed_head_name=request.POST.get('fixed_head_name').upper()

            if request.POST.get('fixed_date'):
                fixededit.fixed_date=request.POST.get('fixed_date')
            else:
                fixededit.fixed_date= fixededit.fixed_date

            fixededit.fixed_amount=request.POST.get('fixed_amt')
            fixededit.fixed_dese=request.POST.get('fixed_dese')
            msg=3
            fixededit.save()

        else:
        
            if request.method =='POST':
                fixedexp_reg=FixedExpence()
                fixedexp_reg.fixed_head_name=request.POST['fixed_head_name'].upper()
                fixedexp_reg.fixed_date=request.POST['fixed_date']
                fixedexp_reg.fixed_amount=request.POST['fixed_amt']
                fixedexp_reg.fixed_dese=request.POST['fixed_dese']
                fixedexp_reg.fixed_status=1
                fixedexp_reg.save()
                msg=1

        fixededit=''
       
        fixedexp=FixedExpence.objects.all()
        content={'msg':msg}
        return render(request,'account/fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
    else:
        return redirect('/')
    

def fixed_edit(request,pk):
    
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        fixededit=FixedExpence.objects.get(id=pk)
        fixedexp=FixedExpence.objects.all()
        content=''
        return render(request,'account/fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
    
    else:
        return redirect('/')

def fixed_delete(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        fixededit=FixedExpence.objects.get(fixed_status=1,id=pk)
        fixededit.delete()
        fixedexp=FixedExpence.objects.all()
        fixededit=''
        msg=2
        content={'msg':msg}
        return render(request,'account/fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
        
    else:
        return redirect('/')
    

    
def fixed_change_status(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
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
        return render(request,'account/fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
        
    else:
        return redirect('/')
    

def company_holoidays(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        comp_holidays=Company_Holidays.objects.all()
        return render(request,'account/company_holidays.html',{'comp_holidays':comp_holidays})
    else:
        return redirect('/')
    

def company_holiday_add(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        if request.method =='POST':
            
            
            if request.POST.get('cmphid'):
                comp_holidays_edit=Company_Holidays.objects.get(id=int(request.POST['cmphid']))
                comp_holidays_edit.ch_sdate=request.POST['cmphsdate']
                comp_holidays_edit.ch_edate=request.POST['cmphedate']
                comp_holidays_edit.ch_no=request.POST['cmphno']

                e = datetime.strptime(request.POST['cmphedate'], '%Y-%m-%d')
                s = datetime.strptime(request.POST['cmphsdate'], '%Y-%m-%d')

                month_days = (e - s).days + 1
                comp_holidays_edit.ch_workno=int(month_days) - int(request.POST['cmphno'])
               
                comp_holidays_edit.save()
                msg=3

            else:
            
                comp_holiday=Company_Holidays()
                comp_holiday.ch_sdate=request.POST['cmphsdate']
                comp_holiday.ch_edate=request.POST['cmphedate']
                comp_holiday.ch_no=request.POST['cmphno']

                #company workdays Calculations
                e = datetime.strptime(request.POST['cmphedate'], '%Y-%m-%d')
                s = datetime.strptime(request.POST['cmphsdate'], '%Y-%m-%d')

                month_days = (e - s).days + 1
                comp_holiday.ch_workno=int(month_days) - int(request.POST['cmphno'])
            
                comp_holiday.save()
                msg=1
            comp_holidays=Company_Holidays.objects.all()
        return render(request,'account/company_holidays.html',{'comp_holidays':comp_holidays,'msg':msg})
    else:
        return redirect('/')


def company_holidy_edit(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        comp_holidays=Company_Holidays.objects.all()
        comp_holidays_edit=Company_Holidays.objects.get(id=pk)
        return render(request,'account/company_holidays.html',{'comp_holidays':comp_holidays,'comp_holidays_edit':comp_holidays_edit})
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
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        
        
        current_year = datetime.now().year

        content={'months':months,'years':years}
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        emp_salary_all=EmployeeSalary.objects.filter(emp_paidstatus=1)

        emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_salary.values_list('empreg_id', flat=True))

        return render(request,'account/salary_expence_form.html',{'emp_reg':emp_reg,
                            'emp_salary':emp_salary,'emp_salary_all':emp_salary_all,'content':content,'current_year':current_year})
    else:
        return redirect('/')
    


def employee_pending_salary(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
       
        
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
            emp_reg=EmployeeRegister.objects.filter(empdofj__lt=startdate,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_sal.values_list('empreg_id', flat=True))
            return render(request,'account/salary_expence_form.html',{'emp_reg':emp_reg,'content':content})
    else:
            return redirect('/')

    

def salary_expence_add(request,pk):
     
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')

        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        
        
        current_year = datetime.now().year

        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)

        content={'months':months,'years':years}

        emp_reg_edit=EmployeeRegister.objects.get(emp_status=1,id=pk)
        # emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        # emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date).exclude(id__in=emp_salary.values_list('empreg_id', flat=True))

        emp_salary_all=EmployeeSalary.objects.filter(emp_paidstatus=1)


        return render(request,'account/salary_expence_form.html',{'emp_reg_edit':emp_reg_edit,
                                'current_year':current_year,'emp_salary':emp_salary,'content':content,'emp_salary_all':emp_salary_all})
    else:
        return redirect('/')
    

def employee_salary_save(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]

        current_year = datetime.now().year

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        
        
        if request.method =='POST':

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

                comp_holiday=Company_Holidays.objects.get(ch_sdate__gte=startdate,ch_edate__lte=enddate)
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
                    msg=3
                
                else:

            
                    emp_reg.emptol_salary= int(emp_reg.emptol_salary) + int(net_salary)
                    emp_reg.emp_salary_status=1
                    emp_reg.save()

                    emp_salary=EmployeeSalary()
                    emp_salary.empreg_id=emp_reg
                
                    m = date(2000, int(request.POST['empsalary_month']), 1).strftime('%B')
                    
                    emp_salary.empsalary_month= m + ' ' + request.POST['empsalary_year']

                    emp_salary.empslaray_date=request.POST['empsalary_date']
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
                    msg=1

                    # Salay Expence adding to IncomeExpence Table
                    if EmployeeSalary.objects.exists():
                    

                        pay_date = datetime.strptime(request.POST['empsalary_date'], '%Y-%m-%d').date()

                        print(pay_date)

                        # Calculate start and end datetime objects for the month corresponding to input_date
                        payfr_date = pay_date.replace(day=1)

                        last_daymonth = payfr_date.replace(day=28) + timedelta(days=4)
                        payto_date = last_daymonth - timedelta(days=last_daymonth.day)

                        print('Pay date:',payfr_date)
                        print('Pay End Date:',payto_date)

                       
                    
                        try:
                            inexp=IncomeExpence.objects.filter(exin_head_name='SALARY',exin_date__gte=payfr_date,exin_date__lte=payto_date).first()
                            sal_exp=EmployeeSalary.objects.filter(empslaray_date__gte=payfr_date,empslaray_date__lte=payto_date,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
                            #sal_exp_last=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1).last()
                            
                            if sal_exp: 

                                if inexp:

                                    inexp.exin_head_name='SALARY'
                                    inexp.exin_amount=sal_exp
                                    inexp.exin_typ=2
                                    inexp.exin_date=payto_date
                                    inexp.exin_status=1
                                    inexp.save()
                                                
                                else:

                                    incexp=IncomeExpence()
                                    incexp.exin_head_name='SALARY'
                                    incexp.exin_amount=sal_exp
                                    incexp.exin_typ=2
                                    incexp.exin_date=payto_date
                                    incexp.exin_status=1
                                    incexp.save()
                            else:
                                print('No Data')

                        except EmployeeSalary.DoesNotExist:
                                print('No Data')

            except Company_Holidays.DoesNotExist:
                msg=2

            emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)

            

            content={'months':months,'years':years} 

            emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
            emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date).exclude(id__in=emp_salary.values_list('empreg_id', flat=True))
            
            emp_salary_all=EmployeeSalary.objects.filter(emp_paidstatus=1)

            return render(request,'account/salary_expence_form.html',{'emp_reg':emp_reg,'current_year':current_year,
                                'msg':msg,'content':content,'emp_salary':emp_salary,'emp_salary_all':emp_salary_all})
    else:
        return redirect('/')
    

def salary_calculate(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
           uid = request.session['uid']
        else:
             return redirect('/')
        
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
                print(net_salary)
                calc=1
                return render(request,'account/result.html',{'net_salary':net_salary,'calc':calc})
            
                
                
        except Company_Holidays.DoesNotExist:
                msg=2
                return render(request,'account/result.html',{'msg':msg})

        

    else:
        return redirect('/')
    

def salary_expence_edit(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
           uid = request.session['uid']
        else:
             return redirect('/')

        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        
        
        current_year = datetime.now().year

        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        emp_salary=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)

  

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

        content={'mn':mn,'ye':ye,'months':months,'years':years,'month_number':month_number}
       

        emp_salary_all=EmployeeSalary.objects.filter(emp_paidstatus=1)


        return render(request,'account/salary_expence_edit.html',{'emp_reg_edit':emp_reg_edit,
                                'current_year':current_year,'emp_salary':emp_salary,'content':content,'emp_salary_all':emp_salary_all,'content':content})

    else:
        return redirect('/')
    


def salary_edit_save(request):
    
    if 'uid' in request.session:
        if request.session.has_key('uid'):
           uid = request.session['uid']
        else:
             return redirect('/')
        
        
        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 
        
        
        if request.method =='POST':

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

                comp_holiday=Company_Holidays.objects.get(ch_sdate__gte=startdate,ch_edate__lte=enddate)
                work_days=int(month_days) - int(comp_holiday.ch_no) 
                leavefull=int(request.POST['leave_full'])
                leavehalf=int(request.POST['leave_half'])
                w_delay=int(request.POST['work_delay'])
                any_other=int(request.POST['other_amt'])
                any_dother=int(request.POST['other_damt'])
                sal_id=int(request.POST['Emp_regsalid'])
                amt=int(request.POST['amt'])
                emp_reg.emptol_salary=int(emp_reg.emptol_salary) - int(amt)
                emp_reg.save()

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

            
                emp_reg.emptol_salary= int(emp_reg.emptol_salary) + int(net_salary)
                emp_reg.emp_salary_status=1
                emp_reg.save()

                emp_salary=EmployeeSalary.objects.get(id=sal_id)
                emp_salary.empreg_id=emp_reg
            
                m = date(2000, int(request.POST['empsalary_month']), 1).strftime('%B')
                
                emp_salary.empsalary_month= m + ' ' + request.POST['empsalary_year']

               
                if request.POST['empsalary_date']:

                    sal_date=request.POST['empsalary_date']
                   

                    pay_date = emp_salary.empslaray_date #datetime.strptime(request.POST['empsalary_date'], '%Y-%m-%d').date()
                    emp_salary.empslaray_date=request.POST['empsalary_date']

                  

                    # Calculate start and end datetime objects for the month corresponding to input_date
                    payfr_date = pay_date.replace(day=1)

                    last_daymonth = payfr_date.replace(day=28) + timedelta(days=4)
                    payto_date = last_daymonth - timedelta(days=last_daymonth.day)

                    print('Pay date:',payfr_date)
                    print('Pay End Date:',payto_date)
                
                    
                    # Here we change the salary expence amount value in expencce income table 

                    try:
                        inexp=IncomeExpence.objects.filter(exin_head_name='SALARY',exin_date__gte=payfr_date,exin_date__lte=payto_date).first()
                        sal_exp=EmployeeSalary.objects.filter(empslaray_date__gte=payfr_date,empslaray_date__lte=payto_date,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
                        
                        sal_exp = int(sal_exp) - int(net_salary)  
                    
                        
                        if sal_exp: 

                            if inexp:

                                inexp.exin_head_name='SALARY'
                                inexp.exin_amount=sal_exp
                                inexp.exin_typ=2
                                inexp.exin_date=payto_date
                                inexp.exin_status=1
                                inexp.save()

                    except EmployeeSalary.DoesNotExist:
                            print('No Data')

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
                sal_date=emp_salary.empslaray_date
                msg=1

                # Salay Expence adding to IncomeExpence Table
                if EmployeeSalary.objects.exists():
                  
                    if request.POST['empsalary_date']:

                        pay_date = datetime.strptime(request.POST['empsalary_date'], '%Y-%m-%d').date()
                    else:
                        pay_date = sal_date 

                  

                    # Calculate start and end datetime objects for the month corresponding to input_date
                    payfr_date = pay_date.replace(day=1)

                    last_daymonth = payfr_date.replace(day=28) + timedelta(days=4)
                    payto_date = last_daymonth - timedelta(days=last_daymonth.day)

                    print('Pay date:',payfr_date)
                    print('Pay End Date:',payto_date)
                
                    

                    try:
                        inexp=IncomeExpence.objects.filter(exin_head_name='SALARY',exin_date__gte=payfr_date,exin_date__lte=payto_date).first()
                        sal_exp=EmployeeSalary.objects.filter(empslaray_date__gte=payfr_date,empslaray_date__lte=payto_date,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        
                        #sal_exp_last=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1).last()
                        
                        if sal_exp: 

                            if inexp:

                                inexp.exin_head_name='SALARY'
                                inexp.exin_amount=sal_exp
                                inexp.exin_typ=2
                                inexp.exin_date=payto_date
                                inexp.exin_status=1
                                inexp.save()
                                            
                            else:

                                incexp=IncomeExpence()
                                incexp.exin_head_name='SALARY'
                                incexp.exin_amount=sal_exp
                                incexp.exin_typ=2
                                incexp.exin_date=payto_date
                                incexp.exin_status=1
                                incexp.save()
                        else:
                            print('No Data')

                    except EmployeeSalary.DoesNotExist:
                            print('No Data')

            except Company_Holidays.DoesNotExist:
                msg=2
            return redirect('salary_expence')  
        return redirect('salary_expence')  
    
    else:
        return redirect('/')


    
    
def all_salary_expence(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
           uid = request.session['uid']
        else:
             return redirect('/')
        salary=EmployeeSalary.objects.filter(emp_paidstatus=1).order_by('empslaray_date')
        return render(request,'account/all_salary_expence.html',{'salary':salary})

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

# def remaining_salary_expence(request):
     
#     if 'uid' in request.session:
#         if request.session.has_key('uid'):
#             uid = request.session['uid']
#         else:
#             return redirect('/')
        
#         current_year = datetime.now().year

       
#         cur_date=datetime.now().date()
#         fr_date=datetime(cur_date.year, cur_date.month, 1).date()
#         last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
#         to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

        
#         emp_salary=EmployeeSalary.objects.filter( Q(empslaray_date__lt=fr_date) | Q(empslaray_date__gte=fr_date,empslaray_date__lte=to_date))
#         print(emp_salary)
#         emp_reg=EmployeeRegister.objects.filter(empdofj__lt=fr_date).exclude(id__in=emp_salary.values_list('empreg_id', flat=True))
#         print(emp_reg)
    
#         #emp_reg=EmployeeRegister.objects.filter(emp_status=1)

#         return render(request,'account/Remaining_salary_Payments.html',{'emp_reg':emp_reg,
#                             'current_year':current_year,'emp_salary':emp_salary})
        
#     else:
#         return redirect('/')


def income_expence_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        exp_income=IncomeExpence.objects.filter(exin_status=1).order_by('exin_date')
        return render(request,'account/income_expence.html',{'exp_income':exp_income})
    else:
        return redirect('/')
    
    
def income_expence_edit(request,inex_edit):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        exp_income=IncomeExpence.objects.get(id=inex_edit)
        return render(request,'account/income_expence_edit.html',{'exp_income':exp_income})
    else:
        return redirect('/')
    

def income_expence_edit_save(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            incom =int(request.POST['exincom'])
            ex_in=IncomeExpence.objects.get(id=incom)
            ex_in.exin_head_name=request.POST['exin_head_name'].upper()
            ex_in.exin_date=request.POST['exin_date']
            ex_in.exin_amount=request.POST['exin_amt']
            ex_in.exin_dese=request.POST['exin_dese']
            ex_in.exin_typ=request.POST['exin_type']
            ex_in.exin_status=1
            ex_in.save()
            msg=1
            exp_income=IncomeExpence.objects.filter(exin_status=1).order_by('exin_date')

        return render(request,'account/income_expence.html',{'msg':msg,'exp_income':exp_income})
    else:
        return redirect('/')

    

def income_expence_add(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            ex_in=IncomeExpence()
            ex_in.exin_head_name=request.POST['exin_head_name'].upper()
            ex_in.exin_date=request.POST['exin_date']
            ex_in.exin_amount=request.POST['exin_amt']
            ex_in.exin_dese=request.POST['exin_dese']
            ex_in.exin_typ=request.POST['exin_type']
            ex_in.exin_status=1
            ex_in.save()
            msg=1
            exp_income=IncomeExpence.objects.filter(exin_status=1).order_by('exin_date')

        return render(request,'account/income_expence.html',{'msg':msg,'exp_income':exp_income})
    else:
        return redirect('/')

    
def income_expence_delete(request,incom_delete):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
       
        ex_in=IncomeExpence.objects.get(id=incom_delete)  
        ex_in.delete()
        msg=2
        exp_income=IncomeExpence.objects.filter(exin_status=1).order_by('exin_date')

        return render(request,'account/income_expence.html',{'msg':msg,'exp_income':exp_income})
    else:
        return redirect('/')


def emp_Register_form(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        current_year = datetime.now().year
       
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        
        dept=Department.objects.filter(dpt_Status=1)
       
        emp_reg=EmployeeRegister.objects.all()
        return render(request,'account/Employee_Register.html',{'current_year':current_year,'dept':dept,'emp_reg':emp_reg,'months':months,'years':years})
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


def emp_reg_edit(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        emp_reg=EmployeeRegister.objects.get(id=pk)
        dept= Department.objects.filter(dpt_Status=1)
        return render(request,'account/Employee_Register_edit.html',{'emp_reg':emp_reg,'dept':dept})
        
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
    

def emp_reg_deactive(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        emp_reg.emp_status=0
        emp_reg.save()
        messages.info(request, emp_reg.empfullName + ' Registration status deactivate')
        return redirect('emp_Register_form')
    else:
        return redirect('/')
    

def emp_reg_reactive(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        emp_reg.emp_status=1
        emp_reg.save()
        messages.info(request, emp_reg.empfullName + ' Registration status activate')
        return redirect('emp_Register_form')
    else:
        return redirect('/')
    

def emp_salary_active(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        emp_reg.emp_salary_status=1
        emp_reg.save()
        messages.info(request, emp_reg.empfullName + ' Salary status activate')
        return redirect('emp_Register_form')
    else:
        return redirect('/')
    

def emp_salary_deactive(request,pk):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        emp_reg.emp_salary_status=0
        emp_reg.save()
        messages.info(request, emp_reg.empfullName + ' Salary status deactivate')
        return redirect('emp_Register_form')
    else:
        return redirect('/')
    

def emp_reg_delete(request,pk):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        emp_reg=EmployeeRegister.objects.get(id=pk)
        name=emp_reg.empfullName
        emp_reg.delete()
        messages.info(request, name + ' All Details Permanently')
        return redirect('emp_Register_form')
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
        emp_reg_edit=EmployeeRegister.objects.get(id=pk)
        salary=EmployeeSalary.objects.filter(empreg_id=pk)
        return render(request,'account/employee_salary_details.html',{'salary':salary,'emp_reg_edit':emp_reg_edit})
    else:
        return redirect('/')
    

def employee_salary_payments_search(request,pk):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            emp_reg_edit=EmployeeRegister.objects.get(id=pk)
            salary=EmployeeSalary.objects.filter(empreg_id=pk,empslaray_date__gte=request.POST['empfr_data'],empslaray_date__lte=request.POST['empto_date'])

        return render(request,'account/employee_salary_details.html',{'salary':salary,'emp_reg_edit':emp_reg_edit})
    else:
        return redirect('/')
    


# Analysis Section 


def analysis(request):

    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        
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


        # ==============================OJT section Start =============================

       

        reg=Register.objects.filter(reg_status=1).count()
        reg_c=Register.objects.filter(dofj__gte=fr_date,dofj__lte=to_date).count()
        reg_c_amt=Register.objects.filter(dofj__gte=fr_date,dofj__lte=to_date,).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']
        reg_ojt_amt=Register.objects.filter(reg_status=1).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']

        reg_pending=Register.objects.filter(reg_status=1,payment_status=0).count()
        reg_complete=Register.objects.filter(reg_status=1,payment_status=1).count()
        reg_incomplete=Register.objects.filter(reg_status=1,payment_status=2).count()
        reg_p_amt=Register.objects.filter(reg_status=1,payment_status=0).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']
        reg_c_amt=Register.objects.filter(reg_status=1,payment_status=1).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']
        reg_in_amt=Register.objects.filter(reg_status=1,payment_status=2).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']

        after_6_days = fr_date + timedelta(days=6)  
        after_8_days = fr_date + timedelta(days=7)  
        after_15days = fr_date + timedelta(days=14) 

        payhistory1=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        payhistory8=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        payhistory15=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        payhistory1_c=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,).count()
        payhistory8_c=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,).count()
        payhistory15_c=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,).count()
      
        unpaidhis=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1)
        reg_upaid_c=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=fr_date,next_pay_date__lte=to_date).exclude(id__in=unpaidhis.values_list('reg_id', flat=True)).count()
        reg_upaid=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=fr_date,next_pay_date__lte=to_date).exclude(id__in=unpaidhis.values_list('reg_id', flat=True)).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        next_reg_upaid_c=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end).count()
        next_reg_upaid=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

       


        # ==============================End OJT section  =============================


        # ============================== Employee section Start =============================

        emp_reg=EmployeeRegister.objects.all().count()
       
        emp_reg_act=EmployeeRegister.objects.filter(emp_status=1).count()
        emp_reg_sal=EmployeeRegister.objects.filter(emp_salary_status=0).count()
        emp_reg_actsal=EmployeeRegister.objects.filter(emp_salary_status=1).count()
        emp_reg_tsal=EmployeeRegister.objects.all().aggregate(Sum('emptol_salary'))['emptol_salary__sum']

        emp_sal_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).count()
        emp_sal=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        
        emp_con_sal=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1).count()
        emp_con_sal_amt=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']
        emp_unp=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        emp_unpaid=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).count()
        emp_unp_amt=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']

        after_14_days = fr_date + timedelta(days=14)  
        after_15_days = fr_date + timedelta(days=15)  
       

        empsalc_1to7=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=after_14_days,emp_paidstatus=1).count()
        empsal_1to7=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=after_14_days,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        empsalc_15to=EmployeeSalary.objects.filter(empslaray_date__gte=after_15_days,empslaray_date__lte=to_date,emp_paidstatus=1).count()
        empsal_15to=EmployeeSalary.objects.filter(empslaray_date__gte=after_15_days,empslaray_date__lte=to_date,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']

        
        

        # ==============================End Employee section  =============================

        #=EmployeeRegister.objects.filter(emp_status=1).count()
        #emp_salary_count=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empdofj__lt=fr_date).count()


        content={
           
                 'next_month_income':next_month_income,'next_month_exp':next_month_exp,'next_balans':next_balans,
                 'income':income,
                 'expence':expence,
                 'balans':balans,
                 'bal_pr':bal_pr,
                 'exp_pr':exp_pr,
                 'cur_date':cur_date,
                 'inc_pr':inc_pr,
                 'reg':reg,'reg_c':reg_c,'reg_c_amt':reg_c_amt,
                 'reg_ojt_amt':reg_ojt_amt,'reg_pending':reg_pending,'reg_complete':reg_complete,
                 'reg_p_amt':reg_p_amt,'reg_c_amt':reg_c_amt,'reg_in_amt':reg_in_amt,'reg_incomplete':reg_incomplete,'reg_upaid_c':reg_upaid_c,'reg_upaid':reg_upaid,
                 'emp_reg_tsal':emp_reg_tsal,'emp_reg':emp_reg,'emp_reg_act':emp_reg_act,'emp_reg_sal':emp_reg_sal,'emp_reg_actsal':emp_reg_actsal,
                 'emp_sal':emp_sal,'emp_sal_count':emp_sal_count,'emp_unpaid':emp_unpaid,'emp_unp_amt':emp_unp_amt,'emp_con_sal':emp_con_sal,'emp_con_sal_amt':emp_con_sal_amt,
                 'empsalc_1to7':empsalc_1to7,'empsal_1to7':empsal_1to7,'empsalc_15to':empsalc_15to,'empsal_15to':empsal_15to,
                 'payhistory1':payhistory1,'payhistory8':payhistory8,'payhistory15':payhistory15,'payhistory1_c':payhistory1_c,'payhistory8_c':payhistory8_c,'payhistory15_c':payhistory15_c,
                 'next_reg_upaid_c':next_reg_upaid_c,'next_reg_upaid':next_reg_upaid,
                 }
       
        return render(request,'account/analysis.html',{'content':content})
    else:
        return redirect('/')
    

def analysis_months(request):
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
        else:
            return redirect('/')
        
        months = [(str(i),date(2000, i, 1).strftime('%B')) for i in range(1, 13)]
        years = [(str(i), str(i)) for i in range(2021, 2031)]
        current_year = datetime.now().year

        content={
            'months':months,'years':years,'current_year':current_year,}
        return render(request,'account/analysis_on_months.html',{'content':content})
    else:
        return redirect('/')
    

def analysis_search(request):
    
    if 'uid' in request.session:
        if request.session.has_key('uid'):
            uid = request.session['uid']
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
            return redirect('analysis_search')
      


        content={
            'month_name':month_name,'months':months,'years':years,'current_year':current_year,'fr_date':fr_date,'to_date':to_date,
            'income':income,'expence':expence,'balans':balans,'exp_pr':exp_pr,'inc_pr':inc_pr,'bal_pr':bal_pr,
            'reg_c':reg_c,'reg_c_amt':reg_c_amt,
            'payhistory1':payhistory1,'payhistory8':payhistory8,'payhistory15':payhistory15,'payhistory1_c':payhistory1_c,'payhistory8_c':payhistory8_c,'payhistory15_c':payhistory15_c,
            'emp_reg':emp_reg,'emp_con_sal_amt':emp_con_sal_amt,'emp_sal_count':emp_sal_count,'emp_sal':emp_sal,
            'empsalc_1to7':empsalc_1to7,'empsal_1to7':empsal_1to7,'empsalc_15to':empsalc_15to,'empsal_15to':empsal_15to,
            }
        return render(request,'account/analysis_on_months.html',{'content':content})
        
    else:
        return redirect('/')


    



# def payment_completed(request,pk):
#     reg=Register.objects.get(id=pk)
#     reg.payment_status=1
#     reg.save()
#     msg=1
#     reg=Register.objects.filter(reg_status=1)
#     return render(request,'account/dashboard.html',{'reg':reg,'msg':msg})

#============================== End Account Module ====================================================================





# ===========================Admin Module Section ======================================


def admin_account(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        user=User.objects.get(id=admid)
        
        return render(request,'Admin/Admin_Account.html',{'user':user})

    else:
            return redirect('/')
    

def admin_password_changeing(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.method=='POST':
            username=request.POST['adurname']
            password=request.POST['adpsw']

            user=User.objects.get(id=admid)
            if username:
                user.username=username
            else:
                user.username= user.username
            user.set_password(password)
            user.save()
            msg=1
        return render(request,'Admin/Admin_Account.html',{'user':user,'msg':msg})

    else:
        return redirect('/')




def admin_dashboard(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        reg=Register.objects.filter(reg_status=0)
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg).count
        reg1=Register.objects.filter(reg_status=1)
        payhis_list=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1)


        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

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

        fixexp=FixedExpence.objects.filter(fixed_date__lte=cur_date,fixed_date__gte=fr_date,fixed_status=1)
                        
        inex = IncomeExpence.objects.filter(exin_date__in=fixexp.values_list('fixed_date', flat=True)).filter(exin_head_name__in=fixexp.values_list('fixed_head_name', flat=True))
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

        return render(request,'Admin/Admin_dashboard.html',{'payhis':payhis,'payhis_list':payhis_list})
    
    else:
        return redirect('/')
    

def admin_trackPayments(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        reg=Register.objects.filter(reg_status=1,payment_status=0)
        cur_date=datetime.now().date()
        return render(request,'Admin/admintrack_Payments.html',{'reg':reg,'cur_date':cur_date})
    
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
        
        reg=Register.objects.filter(reg_status=1)
        payhis=PaymentHistory.objects.all()
        return render(request,'Admin/adminpayments_history.html',{'reg':reg,'payhis':payhis})
            
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



def newpay_confirm_list(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
            
        reg=Register.objects.filter(reg_status=0)
        firstpayhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg).first
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg)
        return render(request,'Admin/newpayment_list.html',{'payhis':payhis,'firstpayhis':firstpayhis})
            
    else:
        return redirect('/')


def view_details(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        firstpayhis=PaymentHistory.objects.get(id=pk)
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0)
        return render(request,'Admin/newpayment_list.html',{'payhis':payhis,'firstpayhis':firstpayhis})
            
    else:
        return redirect('/')
    


def admin_approve(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
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
     

        return redirect('newpay_confirm_list')
            
    else:
        return redirect('/')
    


def admin_confirm(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
            
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

        #next payment calculation

        #cal=int(reg.regtotal_amt / 3)
        #cal2=int(cal) * 2
        
        if reg.fixed_intial_amt == pay_aprove.payintial_amt:
            reg.next_pat_amt = int(reg.regbalance_amt)
            reg.fixed_intial_amt = int(reg.regbalance_amt)

        elif reg.fixed_intial_amt >  pay_aprove.payintial_amt:
            #amt =  int(reg.next_pat_amt) - int(pay_aprove.payintial_amt)

            #if  reg.next_pat_amt < cal and reg.reg_payedtotal < cal2 :
                #reg.next_pat_amt =  cal + amt
            #else:
            reg.next_pat_amt = int(reg.fixed_intial_amt) - int(pay_aprove.payintial_amt)
            reg.fixed_intial_amt = int(reg.fixed_intial_amt) - int(pay_aprove.payintial_amt)

        elif  reg.fixed_intial_amt <  pay_aprove.payintial_amt:
            #amt= int(pay_aprove.payintial_amt) -   int(reg.next_pat_amt) 
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
            
        payhis=PaymentHistory.objects.get(id=pk)
        reg=Register.objects.get(id=payhis.reg_id.id)
        payhis.delete()
        reg.delete()
        firstpayhis=PaymentHistory.objects.filter(admin_payconfirm=0).first
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0)
        return render(request,'Admin/newpayment_list.html',{'payhis':payhis,'firstpayhis':firstpayhis})
            
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
        
        reg=Register.objects.filter(payment_status=0)
        cur_date=datetime.now().date()
        return render(request,'Admin/adminallpaymets.html',{'reg':reg,'cur_date':cur_date})
            
    else:
        return redirect('/')
    

def admin_completed_payments(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        reg=Register.objects.filter(payment_status=1)
        cur_date=datetime.now().date()
        return render(request,'Admin/adminallpaymets.html',{'reg':reg,'cur_date':cur_date})
            
    else:
        return redirect('/')
    


def admin_incompleted_payments(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        reg=Register.objects.filter(payment_status=2)
        cur_date=datetime.now().date()
        return render(request,'Admin/adminallpaymets.html',{'reg':reg,'cur_date':cur_date})
            
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
        dept=Department.objects.all()
        
        return render(request,'Admin/admin_department_form.html',{'dept':dept})
        
    else:
        return redirect('/')
    

def admin_department_add(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        if request.method =='POST':

            if request.POST['dept_id']:
                dept=Department.objects.get(id=int( request.POST['dept_id']))
                dept.department=request.POST['dept_name'].upper()
                dept.save()
                msg=3
            else:

                dept=Department()
                dept.department=request.POST['dept_name'].upper()
                dept.dpt_Status=1
                dept.save()
                msg=1

            dept=Department.objects.all()
        
        return render(request,'Admin/admin_department_form.html',{'dept':dept,'msg':msg})
        
    else:
        return redirect('/')
    
def admin_edit_dept(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
          
        dept_edit=Department.objects.get(id=pk)
      
        dept=Department.objects.all()
        return render(request,'Admin/admin_department_form.html',{'dept':dept,'dept_edit':dept_edit})
    
    else:
        return redirect('/')
          
    
    
def admin_remove_dept(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
          
        dept=Department.objects.get(id=pk)
        dept.delete()
        msg=2
        dept=Department.objects.all()
        
        return render(request,'Admin/admin_department_form.html',{'dept':dept,'msg':msg})
        
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
        dept=Department.objects.filter(dpt_Status=1)
       
        emp_reg=EmployeeRegister.objects.all()
        return render(request,'Admin/admin_Employee_view.html',{'dept':dept,'emp_reg':emp_reg})
        
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
        
        exp_income=IncomeExpence.objects.filter(exin_status=1,).order_by('-id')
        inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1).aggregate(intol=Sum('exin_amount'))['intol']
        expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2).aggregate(exptol=Sum('exin_amount'))['exptol']
       
        content={'inco':inco,'expe':expe}
        return render(request,'Admin/admin_income_expence.html',{'exp_income':exp_income,'content':content})
    else:
        return redirect('/')
    

def admin_income_expence_add(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            ex_in=IncomeExpence()
            ex_in.exin_head_name=request.POST['adexin_head_name'].upper()
            ex_in.exin_date=request.POST['adexin_date']
            ex_in.exin_amount=request.POST['adexin_amt']
            ex_in.exin_dese=request.POST['adexin_dese']
            ex_in.exin_typ=request.POST['adexin_type']
            ex_in.exin_status=1
            ex_in.save()
            msg=1
        exp_income=IncomeExpence.objects.filter(exin_status=1,).order_by('-exin_date')
        inco=IncomeExpence.objects.filter(exin_status=1,exin_typ=1).aggregate(intol=Sum('exin_amount'))['intol']
        expe=IncomeExpence.objects.filter(exin_status=1,exin_typ=2).aggregate(exptol=Sum('exin_amount'))['exptol']
       
        content={'inco':inco,'expe':expe}
        return render(request,'Admin/admin_income_expence.html',{'exp_income':exp_income,'content':content,'msg':msg})
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
        
        return render(request,'Admin/admin_salary_expence.html',{'content':content,'salary':salary,})
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
        
        emp_reg_edit=EmployeeRegister.objects.get(id=pk)
        salary=EmployeeSalary.objects.filter(empreg_id=pk)
        salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empreg_id=pk).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']
        return render(request,'Admin/admin_employee_salary_details.html',{'salary':salary,'emp_reg_edit':emp_reg_edit,'salary_tol':salary_tol})
    else:
        return redirect('/')
    

def admin_employee_salary_payments_search(request,pk):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.method =='POST':

            emp_reg_edit=EmployeeRegister.objects.get(id=pk)
            salary=EmployeeSalary.objects.filter(empreg_id=pk,empslaray_date__gte=request.POST['adempfr_data'],empslaray_date__lte=request.POST['adempto_date'])
            salary_tol=EmployeeSalary.objects.filter(emp_paidstatus=1,empreg_id=pk,empslaray_date__gte=request.POST['adempfr_data'],empslaray_date__lte=request.POST['adempto_date']).aggregate(sal_tol=Sum('emppaid_amt'))['sal_tol']
            return render(request,'Admin/admin_employee_salary_details.html',{'salary':salary,'emp_reg_edit':emp_reg_edit,'salary_tol':salary_tol})

        return render(request,'account/employee_salary_details.html',{'salary':salary,'emp_reg_edit':emp_reg_edit})
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
        
        fixededit=FixedExpence.objects.all()

        if fixededit:

            fixededit=None   

        fixedexp=FixedExpence.objects.all()
        content=''
        return render(request,'Admin/admin_fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
    else:
        return redirect('/')
    
def admin_fixed_expence_add(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.POST['fixed_id']:

            fixededit=FixedExpence.objects.get(fixed_status=1,id=int(request.POST['fixed_id']))
            fixededit.fixed_head_name=request.POST.get('fixed_head_name').upper()

            if request.POST.get('fixed_date'):
                fixededit.fixed_date=request.POST.get('fixed_date')
            else:
                fixededit.fixed_date= fixededit.fixed_date

            fixededit.fixed_amount=request.POST.get('fixed_amt')
            fixededit.fixed_dese=request.POST.get('fixed_dese')
            msg=3
            fixededit.save()

        else:
        
            if request.method =='POST':
                fixedexp_reg=FixedExpence()
                fixedexp_reg.fixed_head_name=request.POST['fixed_head_name'].upper()
                fixedexp_reg.fixed_date=request.POST['fixed_date']
                fixedexp_reg.fixed_amount=request.POST['fixed_amt']
                fixedexp_reg.fixed_dese=request.POST['fixed_dese']
                fixedexp_reg.fixed_status=1
              
                fixedexp_reg.save()
                msg=1

        fixededit=''
       
        fixedexp=FixedExpence.objects.all()
        content={'msg':msg}
        return render(request,'account/fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
    else:
        return redirect('/')
    

def admin_fixed_edit(request,pk):
    
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        fixededit=FixedExpence.objects.get(id=pk)
        fixedexp=FixedExpence.objects.all()
        content=''
        return render(request,'Admin/admin_fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
    
    else:
        return redirect('/')
    

   
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
        fixededit=FixedExpence.objects.get(fixed_status=1,id=pk)
        fixededit.delete()
        fixedexp=FixedExpence.objects.all()
        fixededit=''
        msg=2
        content={'msg':msg}
        return render(request,'Admin/admin_fixed_expence.html',{'fixedexp':fixedexp,'content':content,'fixededit':fixededit})
        
    else:
        return redirect('/')



def admin_company_holoidays(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        comp_holidays=Company_Holidays.objects.all()
        return render(request,'Admin/admin_company_holidays.html',{'comp_holidays':comp_holidays})
    else:
        return redirect('/')
    

def admin_company_holiday_add(request):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
        if request.method =='POST':
            
            
            if request.POST.get('cmphid'):
                comp_holidays_edit=Company_Holidays.objects.get(id=int(request.POST['cmphid']))
                comp_holidays_edit.ch_sdate=request.POST['cmphsdate']
                comp_holidays_edit.ch_edate=request.POST['cmphedate']
                comp_holidays_edit.ch_no=request.POST['cmphno']

                e = datetime.strptime(request.POST['cmphedate'], '%Y-%m-%d')
                s = datetime.strptime(request.POST['cmphsdate'], '%Y-%m-%d')

                month_days = (e - s).days + 1
                comp_holidays_edit.ch_workno=int(month_days) - int(request.POST['cmphno'])
               
                comp_holidays_edit.save()
                msg=3

            else:
            
                comp_holiday=Company_Holidays()
                comp_holiday.ch_sdate=request.POST['cmphsdate']
                comp_holiday.ch_edate=request.POST['cmphedate']
                comp_holiday.ch_no=request.POST['cmphno']

                #company workdays Calculations
                e = datetime.strptime(request.POST['cmphedate'], '%Y-%m-%d')
                s = datetime.strptime(request.POST['cmphsdate'], '%Y-%m-%d')

                month_days = (e - s).days + 1
                comp_holiday.ch_workno=int(month_days) - int(request.POST['cmphno'])
            
                comp_holiday.save()
                msg=1
            comp_holidays=Company_Holidays.objects.all()
        return render(request,'Admin/admin_company_holidays.html',{'comp_holidays':comp_holidays,'msg':msg})
    else:
        return redirect('/')


def admin_company_holidy_edit(request,pk):
    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        comp_holidays=Company_Holidays.objects.all()
        comp_holidays_edit=Company_Holidays.objects.get(id=pk)
        return render(request,'Admin/admin_company_holidays.html',{'comp_holidays':comp_holidays,'comp_holidays_edit':comp_holidays_edit})
    else:
        return redirect('/')
    


# Analysi Section 

def admin_analysis(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
        
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


        # ==============================OJT section Start =============================

       

        reg=Register.objects.filter(reg_status=1).count()
        reg_c=Register.objects.filter(dofj__gte=fr_date,dofj__lte=to_date).count()
        reg_c_amt=Register.objects.filter(dofj__gte=fr_date,dofj__lte=to_date,).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']
        reg_ojt_amt=Register.objects.filter(reg_status=1).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']

        reg_pending=Register.objects.filter(reg_status=1,payment_status=0).count()
        reg_complete=Register.objects.filter(reg_status=1,payment_status=1).count()
        reg_incomplete=Register.objects.filter(reg_status=1,payment_status=2).count()
        reg_p_amt=Register.objects.filter(reg_status=1,payment_status=0).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']
        reg_c_amt=Register.objects.filter(reg_status=1,payment_status=1).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']
        reg_in_amt=Register.objects.filter(reg_status=1,payment_status=2).aggregate(Sum('regtotal_amt'))['regtotal_amt__sum']

        after_6_days = fr_date + timedelta(days=6)  
        after_8_days = fr_date + timedelta(days=7)  
        after_15days = fr_date + timedelta(days=14) 

        payhistory1=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        payhistory8=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        payhistory15=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        payhistory1_c=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,).count()
        payhistory8_c=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,).count()
        payhistory15_c=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,).count()
      
        unpaidhis=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1)
        reg_upaid_c=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=fr_date,next_pay_date__lte=to_date).exclude(id__in=unpaidhis.values_list('reg_id', flat=True)).count()
        reg_upaid=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=fr_date,next_pay_date__lte=to_date).exclude(id__in=unpaidhis.values_list('reg_id', flat=True)).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
        next_reg_upaid_c=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end).count()
        next_reg_upaid=Register.objects.filter(reg_status=1,payment_status=0,next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

       


        # ==============================End OJT section  =============================


        # ============================== Employee section Start =============================

        emp_reg=EmployeeRegister.objects.all().count()
       
        emp_reg_act=EmployeeRegister.objects.filter(emp_status=1).count()
        emp_reg_sal=EmployeeRegister.objects.filter(emp_salary_status=0).count()
        emp_reg_actsal=EmployeeRegister.objects.filter(emp_salary_status=1).count()
        emp_reg_tsal=EmployeeRegister.objects.all().aggregate(Sum('emptol_salary'))['emptol_salary__sum']

        emp_sal_count=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).count()
        emp_sal=EmployeeSalary.objects.filter(emp_paidstatus=1,empslaray_date__gte=fr_date,empslaray_date__lte=to_date).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        
        emp_con_sal=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1).count()
        emp_con_sal_amt=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']
        emp_unp=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date)
        emp_unpaid=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).count()
        emp_unp_amt=EmployeeRegister.objects.filter(empdofj__lt=fr_date,emp_status=1,emp_salary_status=1,).exclude(id__in=emp_unp.values_list('empreg_id', flat=True)).aggregate(Sum('empconfirmsalary'))['empconfirmsalary__sum']

        after_14_days = fr_date + timedelta(days=14)  
        after_15_days = fr_date + timedelta(days=15)  
       

        empsalc_1to7=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=after_14_days,emp_paidstatus=1).count()
        empsal_1to7=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=after_14_days,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
        empsalc_15to=EmployeeSalary.objects.filter(empslaray_date__gte=after_15_days,empslaray_date__lte=to_date,emp_paidstatus=1).count()
        empsal_15to=EmployeeSalary.objects.filter(empslaray_date__gte=after_15_days,empslaray_date__lte=to_date,emp_paidstatus=1).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']

        
        

        # ==============================End Employee section  =============================

        #=EmployeeRegister.objects.filter(emp_status=1).count()
        #emp_salary_count=EmployeeRegister.objects.filter(emp_status=1,emp_salary_status=1,empdofj__lt=fr_date).count()


        content={
           
                 'next_month_income':next_month_income,'next_month_exp':next_month_exp,'next_balans':next_balans,
                 'income':income,
                 'expence':expence,
                 'balans':balans,
                 'bal_pr':bal_pr,
                 'exp_pr':exp_pr,
                 'cur_date':cur_date,
                 'inc_pr':inc_pr,
                 'reg':reg,'reg_c':reg_c,'reg_c_amt':reg_c_amt,
                 'reg_ojt_amt':reg_ojt_amt,'reg_pending':reg_pending,'reg_complete':reg_complete,
                 'reg_p_amt':reg_p_amt,'reg_c_amt':reg_c_amt,'reg_in_amt':reg_in_amt,'reg_incomplete':reg_incomplete,'reg_upaid_c':reg_upaid_c,'reg_upaid':reg_upaid,
                 'emp_reg_tsal':emp_reg_tsal,'emp_reg':emp_reg,'emp_reg_act':emp_reg_act,'emp_reg_sal':emp_reg_sal,'emp_reg_actsal':emp_reg_actsal,
                 'emp_sal':emp_sal,'emp_sal_count':emp_sal_count,'emp_unpaid':emp_unpaid,'emp_unp_amt':emp_unp_amt,'emp_con_sal':emp_con_sal,'emp_con_sal_amt':emp_con_sal_amt,
                 'empsalc_1to7':empsalc_1to7,'empsal_1to7':empsal_1to7,'empsalc_15to':empsalc_15to,'empsal_15to':empsal_15to,
                 'payhistory1':payhistory1,'payhistory8':payhistory8,'payhistory15':payhistory15,'payhistory1_c':payhistory1_c,'payhistory8_c':payhistory8_c,'payhistory15_c':payhistory15_c,
                 'next_reg_upaid_c':next_reg_upaid_c,'next_reg_upaid':next_reg_upaid,
                 }
       
        return render(request,'Admin/admin_analysis.html',{'content':content})
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

