from django.shortcuts import redirect, render
from django.contrib import messages
from payment_app.models import *
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User,auth
from datetime import datetime


def login(request):
    return render(request, 'login.html')


# Admin Module Section


def dashboard(request):
    return render(request,'account/dashboard.html')

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
            reg.dept_id=Department.objects.get(id=request.POST['dept'])
        
            reg.save()
            payhis=PaymentHistory()
            payhis.head_name='First Payment'
            payhis.payintial_amt=int(request.POST['init_amunt'])
            payhis.paytotal_amt=int(request.POST['tot_amount'])
            a1=int(request.POST['init_amunt'])
            t1=int(request.POST['tot_amount'])
            tol=t1-a1
            if tol > 0:
                payhis.paybalance_amt=tol
                reg.regbalance_amt=tol
            else:
                  payhis.paybalance_amt=0
                  reg.regbalance_amt=0

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
    reg=Register.objects.get(id=pk, reg_status=0)
    reg.reg_status=1
    reg.save()
    dept=Department.objects.filter(dpt_Status=1)
    reg=Register.objects.filter(reg_status=0)
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
     

# Account Module Section
