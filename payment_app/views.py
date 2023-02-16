from django.shortcuts import redirect, render
from django.contrib import messages
from payment_app.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,auth
from datetime import datetime


def login(request):
    return render(request, 'login.html')


def login_dashboard(request):
    return render(request,'Admin/Admin_dashboard.html')




# Account Module Section


def dashboard(request):
    reg=Register.objects.filter(reg_status=1)
    return render(request,'account/dashboard.html',{'reg':reg})

def department_form(request):
    dept=Department.objects.all()
    return render(request,'account/Department_form.html',{'dept':dept})


def department_add(request):
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
    
    
def pyment_form(request):
    reg=Register.objects.filter(reg_status=1)
    return render(request,'account/Payment_form.html',{'reg':reg})

def addpayment_details(request,pk):
    reg_dt=Register.objects.get(id=pk)
    reg=Register.objects.filter(reg_status=1)
    return render(request,'account/Payment_form.html',{'reg':reg,'reg_dt':reg_dt})

def save_payment(request):
    if request.method =='POST':
        paymt=PaymentHistory()
        reg=Register.objects.get(id=int(request.POST['payname']))
        paymt.reg_id=reg
        paymt.head_name=request.POST['payhname']
        paymt.payintial_amt=int(request.POST['pinit_amunt'])

        if request.POST['pdfj']:
            paymt.paydofj=request.POST['pdfj']
        pay_amt=int(request.POST['pinit_amunt'])
        paymt.paybalance_amt=int(reg.regbalance_amt) - pay_amt
        paymt.paytotal_amt=int(reg.regtotal_amt)
        paymt.save()
        reg.payprogress=int(request.POST['progres'])
        reg.save()
        msg=1
        reg=Register.objects.filter(reg_status=1)
        return render(request,'account/Payment_form.html',{'reg':reg,'msg':msg})


def payment_details(request,pk):
    pay_dt=PaymentHistory.objects.filter(reg_id_id=pk)
    reg=Register.objects.filter(reg_status=1)
    return render(request,'account/Payment_form.html',{'reg':reg,'pay_dt':pay_dt})
    
    


def remove_dept(request,pk):
    dept=Department.objects.get(id=pk)
    dept.delete()
    msg=2
    dept=Department.objects.all()
    return render(request,'account/Department_form.html',{'msg':msg,'dept':dept})
     
     

def Register_form(request):
    # if 'uid' in request.session:
    #     if request.session.has_key('uid'):
    #         uid = request.session['uid']
    #     else:
    #         return redirect('/')
        dept=Department.objects.filter(dpt_Status=1)
        reg=Register.objects.filter(reg_status=0)
        payhis=PaymentHistory.objects.all()
        return render(request,'account/Register_form.html',{'dept':dept,'reg':reg,'payhis':payhis})
    # else:
    #     return redirect('login')

def register_Details(request):
    # if 'uid' in request.session:
    #     if request.session.has_key('uid'):
    #         uid = request.session['uid']
    #     else:
    #         return redirect('/')
        dept=Department.objects.all()

        if request.method =='POST':
            reg=Register()
            reg.fullName=request.POST['name']
            reg.Phone=request.POST['phno']
            reg.dofj=request.POST['dfj']
            reg.refrence=request.POST['refby']
            reg.regtotal_amt=int(request.POST['tot_amount'])
            reg.dept_id=Department.objects.get(id=request.POST['dept'])
        
            reg.save()
            payhis=PaymentHistory()
            payhis.head_name='First Payment'
            payhis.payintial_amt=int(request.POST['init_amunt'])
            payhis.paytotal_amt=int(request.POST['tot_amount'])
            

            payhis.pay_status=1
            payhis.reg_id=reg
            payhis.save()

            reg.firstpay_id=payhis.id
            reg.save()
            msg=1
            reg=Register.objects.filter(reg_status=0)
            payhis=PaymentHistory.objects.all()
            return render(request,'account/Register_form.html',{'msg':msg,'dept':dept,'reg':reg,'payhis':payhis})
        else:
            return redirect('Register_form')
    # else:
    #     return redirect('login')


def confirm(request,pk):
    reg1=Register.objects.get(id=pk, reg_status=0)
    reg1.reg_status=1
   
    dept=Department.objects.filter(dpt_Status=1)
    reg=Register.objects.filter(reg_status=0)
    payhis=PaymentHistory.objects.get(reg_id_id=reg1.id)
    reg1.regbalance_amt=int(reg1.regtotal_amt) - int(payhis.payintial_amt)
    reg1.save()

    payhis.pay_status=1
    payhis.paybalance_amt=int(reg1.regbalance_amt)
    payhis.save()

    payhis=PaymentHistory.objects.all()
    msg=2
    return render(request,'account/Register_form.html',{'msg':msg,'dept':dept,'reg':reg,'payhis':payhis})


def remove(request,pk):
    reg=Register.objects.get(id=pk)
    reg.reg_status=2
    reg.delete()
    dept=Department.objects.filter(dpt_Status=1)
    reg=Register.objects.filter(reg_status=0)
    payhis=PaymentHistory.objects.all()
    msg=3
    return render(request,'account/Register_form.html',{'msg':msg,'dept':dept,'reg':reg,'payhis':payhis})
     

# Admin Module Section

def admin_dashboard(request):
    reg=Register.objects.filter(reg_status=0)
    payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg).count
    return render(request,'Admin/Admin_dashboard.html',{'payhis':payhis})

def newpay_confirm_list(request):
    reg=Register.objects.filter(reg_status=0)
    firstpayhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg).first
    payhis=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg)
    return render(request,'Admin/newpayment_list.html',{'payhis':payhis,'firstpayhis':firstpayhis})


def view_details(request,pk):
    firstpayhis=PaymentHistory.objects.get(id=pk)
    payhis=PaymentHistory.objects.filter(admin_payconfirm=0)
    return render(request,'Admin/newpayment_list.html',{'payhis':payhis,'firstpayhis':firstpayhis})

def admin_approve(request,pk):
    pay_aprove=PaymentHistory.objects.get(id=pk)
    pay_aprove.admin_payconfirm=1
    pay_aprove.pay_status=1
    pay_aprove.save()
    reg=Register.objects.get(id=pay_aprove.reg_id_id)
    reg.regbalance_amt= int(reg.regtotal_amt - pay_aprove.payintial_amt)
    reg.save()
    return redirect('newpay_confirm_list')
     

def admin_remove(request,pk):
    payhis=PaymentHistory.objects.get(id=pk)
    reg=Register.objects.get(id=payhis.reg_id)
    payhis.delete()
    reg.delete()
    firstpayhis=PaymentHistory.objects.filter(admin_payconfirm=0).first
    payhis=PaymentHistory.objects.filter(admin_payconfirm=0)
    return render(request,'Admin/newpayment_list.html',{'payhis':payhis,'firstpayhis':firstpayhis})
     
     
