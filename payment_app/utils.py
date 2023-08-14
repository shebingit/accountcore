from payment_app.models import *



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