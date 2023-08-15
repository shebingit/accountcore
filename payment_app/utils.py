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