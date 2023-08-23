from payment_app.models import *
import datetime 
import calendar
from datetime import datetime,timedelta
from django.db.models import Sum



def nav_data(request):

    reg1=Register.objects.filter(reg_status=1)
    payhis_list=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1)
    approvels=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1)
    approve_count=PaymentHistory.objects.filter(admin_payconfirm=0,reg_id__in=reg1).count()
 
    states = Register_State.objects.filter(allocate_status=1)

    comman_data={'payhis_list':payhis_list,
                 'approvels':approvels,
                 'approve_count':approve_count,
                 'states':states
                 }
    return comman_data




# adding income ,expence and fixed expence  to table 


def income_expence_check(request):
     
    cur_date=datetime.now().date() # Current date 
    fr_date=datetime(cur_date.year, cur_date.month, 1).date()
    last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
    to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 

    states = Register_State.objects.filter(allocate_status=1)
      
    #Income adding to IncomeExpence Table
    if PaymentHistory.objects.exists():
       
        for state in states:
           
            payhis=PaymentHistory.objects.filter(paydofj__gte=fr_date,paydofj__lte=to_date,admin_payconfirm=1,pay_state=state).aggregate(Sum('payintial_amt'))['payintial_amt__sum']
                                

            if payhis:

                try:
                    inexpe=IncomeExpence.objects.get(exin_head_name='OJT',exin_date__gte=fr_date,exin_date__lte=to_date,exin_state=state)

                    inexpe.exin_head_name='OJT'
                    inexpe.exin_amount=payhis
                    inexpe.exin_typ=1
                    inexpe.exin_date=to_date
                    inexpe.exin_status=1
                    inexpe.exin_state=state
                    inexpe.save()
                
                except IncomeExpence.DoesNotExist:

               
                    incexpence=IncomeExpence()
                    incexpence.exin_head_name='OJT'
                    incexpence.exin_amount=payhis
                    incexpence.exin_typ=1
                    incexpence.exin_date=cur_date
                    incexpence.exin_status=1
                    incexpence.exin_state=state
                    incexpence.save()

                                        
            else:
                print('Payment History Is Amount Empty')
    else:
        print('Payment History Is Empty')

                       
    # Salay Expence adding to IncomeExpence Table
    if EmployeeSalary.objects.exists():

        for state in states:

            emp = EmployeeRegister.objects.filter(empstate=state.state_name)
           
            sal_exp=EmployeeSalary.objects.filter(empslaray_date__gte=fr_date,empslaray_date__lte=to_date,emp_paidstatus=1,empreg_id__in=emp).aggregate(Sum('emppaid_amt'))['emppaid_amt__sum']
                                
                                
            if sal_exp:
                try:
                    inexp=IncomeExpence.objects.get(exin_head_name='SALARY',exin_date__gte=fr_date,exin_date__lte=to_date,exin_state=state)
                
              
                    inexp.exin_head_name='SALARY'
                    inexp.exin_amount=sal_exp
                    inexp.exin_typ=2
                    inexp.exin_date=to_date
                    inexp.exin_status=1
                    inexp.exin_state=state
                    inexp.save()
                                    
                except IncomeExpence.DoesNotExist:

                    incexp=IncomeExpence()
                    incexp.exin_head_name='SALARY'
                    incexp.exin_amount=sal_exp
                    incexp.exin_typ=2
                    incexp.exin_date=cur_date
                    incexp.exin_status=1
                    incexp.exin_state=state
                    incexp.save()
            else:
                print('Employee Salary Is Amount Empty')
        else:
            print('Employee Salary Is Empty')

    
    # Fixed Expence adding to the IncomeEpence Table

    for state in states:

        fixexp=FixedExpence.objects.filter(fixed_date__lte=cur_date,fixed_date__gte=fr_date,fixed_status=1,fixed_state=state)
                            
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

    success_msg='Income Expence Details add.'
    return success_msg                  
                                    


# To get all the payments list of selected OJT trainee

def OJT_payments_details(request,pk):
      
    reg=Register.objects.get(id=pk,reg_status=1)
    payhis_list=PaymentHistory.objects.filter(admin_payconfirm=1,reg_id=reg)
    payhis_count=PaymentHistory.objects.filter(admin_payconfirm=1,reg_id=reg).count()

    payments_data={'reg':reg,
                   'payhis_list':payhis_list,
                   'payhis_count':payhis_count}

    return payments_data


#Upcoming payments list

def upcoming_payments(request):

     # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 


        #------------------ Next Month----------------------------

        next_month = cur_date.replace(day=28) + timedelta(days=4)  # get the next month by adding 4 days to the 28th day
        next_month_start = next_month.replace(day=1)  # get the first day of the next month
        next_month_end = next_month_start.replace(day=28) - timedelta(days=1)  # get the last day of the next month by subtracting 1 day from the 28th day
    
        after_6_days = fr_date + timedelta(days=6)
        after_8_days = (fr_date + timedelta(days=7))
        after_15days = (fr_date + timedelta(days=14))
       

        pay_current=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,reg_status=1)
        pay_current_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,reg_status=1).count()
        pay_current_amt=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,reg_status=1).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

        pay1_7=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,reg_status=1)
        pay1_7_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,reg_status=1).count()
        pay1_7_amt=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,reg_status=1).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

        pay8_15=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,reg_status=1)
        pay8_15_count=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,reg_status=1).count()
        pay8_15_amt=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,reg_status=1).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
       
        pay15_end=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,reg_status=1)
        pay15_end_count=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,reg_status=1).count()
        pay15_end_amt=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,reg_status=1).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

        paynext=Register.objects.filter(next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end,reg_status=1)
        paynext_count=Register.objects.filter(next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end,reg_status=1).count()
        paynext_amt=Register.objects.filter(next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end,reg_status=1).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

       

        upcoming_paylist = {
                   'pay_current':pay_current,
                   'pay_current_count':pay_current_count,
                   'pay_current_amt':pay_current_amt,
                   'pay1_7':pay1_7,
                   'pay1_7_count':pay1_7_count,
                   'pay1_7_amt':pay1_7_amt,
                   'pay8_15':pay8_15,'pay8_15_count':pay8_15_count,
                   'pay8_15_amt':pay8_15_amt,
                   'pay15_end':pay15_end,
                   'pay15_end_count':pay15_end_count,
                   'pay15_end_amt':pay15_end_amt,
                   'paynext':paynext,
                   'paynext_count':paynext_count,
                   'paynext_amt':paynext_amt

        }

        return upcoming_paylist



#Upcoming payments list by state

def upcoming_state_payments(request,state):
     
          # --------------------Current month --------------------

        cur_date=datetime.now().date()
        fr_date=datetime(cur_date.year, cur_date.month, 1).date()
        last_day_of_month = calendar.monthrange(cur_date.year, cur_date.month)[1]
        to_date = datetime(cur_date.year, cur_date.month, last_day_of_month).date() 


        #------------------ Next Month----------------------------

        next_month = cur_date.replace(day=28) + timedelta(days=4)  # get the next month by adding 4 days to the 28th day
        next_month_start = next_month.replace(day=1)  # get the first day of the next month
        next_month_end = next_month_start.replace(day=28) - timedelta(days=1)  # get the last day of the next month by subtracting 1 day from the 28th day
    
        after_6_days = fr_date + timedelta(days=6)
        after_8_days = (fr_date + timedelta(days=7))
        after_15days = (fr_date + timedelta(days=14))
       

        pay_current=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,reg_status=1,reg_state=state)
        pay_current_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,reg_status=1,reg_state=state).count()
        pay_current_amt=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=to_date,reg_status=1,reg_state=state).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

        pay1_7=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,reg_status=1,reg_state=state)
        pay1_7_count=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,reg_status=1,reg_state=state).count()
        pay1_7_amt=Register.objects.filter(next_pay_date__gte=fr_date,next_pay_date__lte=after_6_days,reg_status=1,reg_state=state).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

        pay8_15=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,reg_status=1,reg_state=state)
        pay8_15_count=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,reg_status=1,reg_state=state).count()
        pay8_15_amt=Register.objects.filter(next_pay_date__gte=after_8_days,next_pay_date__lte=after_15days,reg_status=1,reg_state=state).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']
       
        pay15_end=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,reg_status=1,reg_state=state)
        pay15_end_count=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,reg_status=1,reg_state=state).count()
        pay15_end_amt=Register.objects.filter(next_pay_date__gte=after_15days,next_pay_date__lte=to_date,reg_status=1,reg_state=state).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

        paynext=Register.objects.filter(next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end,reg_status=1,reg_state=state)
        paynext_count=Register.objects.filter(next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end,reg_status=1,reg_state=state).count()
        paynext_amt=Register.objects.filter(next_pay_date__gte=next_month_start,next_pay_date__lte=next_month_end,reg_status=1,reg_state=state).aggregate(Sum('next_pat_amt'))['next_pat_amt__sum']

       
        state_name=Register_State.objects.get(id=state.id)

        upcoming_state_paylist = {
                   'pay_current':pay_current,
                   'pay_current_count':pay_current_count,
                   'pay_current_amt':pay_current_amt,
                   'pay1_7':pay1_7,
                   'pay1_7_count':pay1_7_count,
                   'pay1_7_amt':pay1_7_amt,
                   'pay8_15':pay8_15,'pay8_15_count':pay8_15_count,
                   'pay8_15_amt':pay8_15_amt,
                   'pay15_end':pay15_end,
                   'pay15_end_count':pay15_end_count,
                   'pay15_end_amt':pay15_end_amt,
                   'paynext':paynext,
                   'paynext_count':paynext_count,
                   'paynext_amt':paynext_amt,
                   'stateName':state_name

        }

        return upcoming_state_paylist