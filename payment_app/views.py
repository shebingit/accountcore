from django.shortcuts import redirect, render
from django.contrib import messages
from payment_app.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from datetime import datetime,timedelta
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from num2words import num2words
import calendar
from django.core.mail import send_mail


#login Section
def login_page(request):
    return render(request, 'login.html')




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
                tk_amount=tk_amount + int(i.reg_payedtotal)

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
                tk_amount=tk_amount + int(i.reg_payedtotal)

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
                tk_amount=tk_amount + int(i.reg_payedtotal)

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
                tk_amount=tk_amount + int(i.reg_payedtotal)

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
            cal=total_amt / 3

            paymt.reg_id=reg
            paymt.head_name=request.POST['payhname']
            paymt.payintial_amt=pay_amt

            next_date=request.POST['pnxtpdof']
            if next_date:
                reg.next_pay_date=request.POST['pnxtpdof']

            else:
                # Calculate the date after 30 days
            
                current_date = reg.next_pay_date

                if pay_amt >= cal:
                
                    after_days = current_date + timedelta(days=30)
                else:
                    after_days = current_date + timedelta(days=15)

                reg.next_pay_date=after_days

        
            paymt.paydofj=request.POST['pdfj']
            pay_amt=int(request.POST['pinit_amunt'])
            paymt.paybalance_amt=int(reg.regbalance_amt) - pay_amt
            paymt.paytotal_amt=int(reg.regtotal_amt)
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
            cal=total_amt / 3
          
            reg.next_pat_amt=cal
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
        
        return render(request,'Admin/Admin_Account.html')

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
                tk_amount=tk_amount + int(i.reg_payedtotal)

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
                tk_amount=tk_amount + int(i.reg_payedtotal)

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
                tk_amount=tk_amount + int(i.reg_payedtotal)

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
                tk_amount=tk_amount + int(i.reg_payedtotal)

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
        reg=Register.objects.get(id=pay_aprove.reg_id_id)
        reg.regbalance_amt= int(reg.regtotal_amt - pay_aprove.payintial_amt)
        pay_aprove.paybalance_amt=int( reg.regbalance_amt)
        pay_aprove.save()
        reg.reg_payedtotal=int(pay_aprove.payintial_amt)
        reg.reg_status=1

        #next payment calculation

        cal=reg.regtotal_amt / 3
        
        if reg.next_pat_amt == pay_aprove.payintial_amt:
            reg.next_pat_amt = cal

        elif reg.next_pat_amt >  pay_aprove.payintial_amt:
            reg.next_pat_amt =  int(reg.next_pat_amt) - int(pay_aprove.payintial_amt)

        elif  reg.next_pat_amt <  pay_aprove.payintial_amt:
            amt= int(pay_aprove.payintial_amt) -   int(reg.next_pat_amt) 
            reg.next_pat_amt = int(cal) - int(amt)

        else:
            print('error')


        if reg.regbalance_amt <= 0:
            reg.next_pay_date=None
            reg.next_pat_amt = 0
            reg.payment_status=1
            reg.payprogress=100
        reg.save()
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

        cal=reg.regtotal_amt / 3
        
        if reg.next_pat_amt == pay_aprove.payintial_amt:
            reg.next_pat_amt = cal

        elif reg.next_pat_amt >  pay_aprove.payintial_amt:
            amt =  int(reg.next_pat_amt) - int(pay_aprove.payintial_amt)

            if  reg.next_pat_amt < cal:
                reg.next_pat_amt =  cal + amt
            else:
                reg.next_pat_amt = int(reg.next_pat_amt) - int(pay_aprove.payintial_amt)


        elif  reg.next_pat_amt <  pay_aprove.payintial_amt:
            amt= int(pay_aprove.payintial_amt) -   int(reg.next_pat_amt) 
            reg.next_pat_amt = int(cal) - int(amt)

        else:
            print('error')

        reg.save()

        if reg.regbalance_amt <= 0:
            reg.next_pay_date=None
            reg.payment_status=1
            reg.next_pat_amt = 0
            reg.save()

        pay_aprove.paybalance_amt= int(reg.regbalance_amt)
        pay_aprove.paytotal_amt=int(reg.regtotal_amt)
        pay_aprove.paybalance_amt=int(reg.regbalance_amt)
        pay_aprove.save()
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
        reg=Register.objects.get(id=payhis.reg_id)
        payhis.delete()
        reg.delete()
        firstpayhis=PaymentHistory.objects.filter(admin_payconfirm=0).first
        payhis=PaymentHistory.objects.filter(admin_payconfirm=0)
        return render(request,'Admin/newpayment_list.html',{'payhis':payhis,'firstpayhis':firstpayhis})
            
    else:
        return redirect('/')


#Search Data using From Date and To Date 

def Search_data(request):

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
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

    if 'admid' in request.session:
        if request.session.has_key('admid'):
            admid = request.session['admid']
        else:
            return redirect('/')
            
        if request.method =='POST':
            payhis=PaymentHistory.objects.filter(paydofj__gte=request.POST['fr_data'],paydofj__lte=request.POST['to_date'])
            return render(request,'account/paymentsfull_View.html',{'payhis':payhis})
        else:
            return redirect('paymentfull_view')
            
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


# =========================== End Admin Module Section ======================================


# LogOut Section

def logout_page(request):
    logout(request)
    return redirect('login_page')
        

# Receipt Download single data
def singeldata_receipt(request,pk):

    date = datetime.now().date()   
    payhis = PaymentHistory.objects.get(id=pk)
    number_in_words = num2words(payhis.payintial_amt)
    template_path = 'account/singledata_Receipt.html'
    context = {'payhis': payhis,
               'number_in_words':number_in_words,
    'media_url':settings.MEDIA_URL,
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
    number_in_words = num2words(reg.reg_payedtotal)
    template_path = 'account/singleUser_full_Receipt.html'
    context = {'reg': reg,
               'payhis':payhis,
               'number_in_words':number_in_words,
    'media_url':settings.MEDIA_URL,
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

