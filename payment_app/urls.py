from django.urls import path 
from.import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

    path('',views.login,name='login'),
    path('Login-Dashboard',views.login_dashboard,name='login_dashboard'),
    path('Admin-Dashboard',views.admin_dashboard,name='admin_dashboard'),

    #account
    path('Account-Dashboard',views.dashboard,name='dashboard'),
    path('All-Payments',views.allpayments,name='allpayments'),
    path('Pending-Payments',views.pending_payments,name='pending_payments'),
    path('Completed-Payments',views.completed_payments,name='completed_payments'),
    path('Incompleted-Payments',views.incompleted_payments,name='incompleted_payments'),
    path('Next-Payments',views.track_payments,name='track_payments'),
    path('Upcoming-Payments',views.upcoming_payments_list,name='upcoming_payments_list'),
    path('Payments-Search',views.paysearch,name='paysearch'),

    
    
    
    path('Users-List',views.Users_list,name='Users_list'),
    path('Edit-User/<int:pk>',views.edit_user,name="edit_user"),
    path('Edit-User-Details/<int:pk>',views.edit_Details,name="edit_Details"),
    path('Edit-Register-User/<int:pk>',views.register_edit,name="register_edit"),
    path('Edit-Register-Save/<int:pk>',views.register_edit_save,name="register_edit_save"),
    
    
    
    
    
    path('Payment-Add',views.pyment_form,name='pyment_form'),
    path('Add-Pay-Details/<int:pk>',views.addpayment_details,name="addpayment_details"),
    path('Pay-Details/<int:pk>',views.payment_details,name="payment_details"),
    path('Payment-Save',views.save_payment,name='save_payment'),

    #Search Data based on Date
    
    path('Search',views.Search_data,name='Search_data'),
    path('Search-Full',views.Search_data_full,name='Search_data_full'),
     
    
    
    path('Department-Form',views.department_form,name='department_form'),
    path('Add-Department',views.department_add,name='department_add'),
    path('Remove-Department/<int:pk>',views.remove_dept,name="remove_dept"),

    # Payments History section
    path('Payments-List',views.pyments_history,name='pyments_history'),
    path('PaymentsView-List',views.paymentfull_view,name='paymentfull_view'),
    
    path('User-Payments-Details/<int:pk>',views.singleuser_details,name="singleuser_details"),
    path('Previous-Details/<int:pk>',views.previous_data,name="previous_data"),
    path('Next-Payments-Details/<int:pk>',views.next_data,name="next_data"),
    
    path('Deactive-User/<int:pk>',views.deactive_user,name="deactive_user"),
    path('Reactive-User/<int:pk>',views.reactivate_user,name="reactivate_user"),
    path('Delete-User/<int:pk>',views.delete_user,name="delete_user"),
    
    
    #Receipt Sigle data 
    path('Payment-Recipt/<int:pk>',views.singeldata_receipt,name="singeldata_receipt"),
    path('Full-Payment-Recipt/<int:pk>',views.singelUserfull_receipt,name="singelUserfull_receipt"),
    

    

    

    path('Register-Form',views.Register_form,name='Register_form'),
    path('Register-Save',views.register_Details,name='register_Details'),
    #path('Confirm/<int:pk>',views.confirm,name="confirm"),
    path('Remove/<int:pk>',views.remove,name="remove"),
    #path('Payment-Completed/<int:pk>',views.payment_completed,name="payment_completed"),
    
    

    #========================== Admin ==============================================

    path('New-Payments-List',views.newpay_confirm_list,name='newpay_confirm_list'),
    path('Payment-Track',views.admin_trackPayments,name='admin_trackPayments'),
    path('Admin-Upcoming-Payments',views.adminupcomingPayments,name='adminupcomingPayments'),
    path('Admin-Payments-View',views.admin_paymentsview,name='admin_paymentsview'),
    path('Admin-Payments-FullView',views.adminpaymentfull_view,name='adminpaymentfull_view'),
    path('Admin-Payments-Search',views.adminsearch_data_full,name='adminsearch_data_full'),
    
    
    path('Admin-User-List',views.admin_user_list,name='admin_user_list'),
    path('Admin-AllUser-Payments',views.admin_allpayments_list,name='admin_allpayments_list'),
    path('Admin-Pending-Payments',views.admin_pending_payments,name='admin_pending_payments'),
    path('Admin-Completed-Payments',views.admin_completed_payments,name='admin_completed_payments'),
    path('Admin-Incompleted-Payments',views.admin_incompleted_payments,name='admin_incompleted_payments'),
    path('Admin-Payment-Search',views.adminpaysearch,name='adminpaysearch'),
    
    
    
    
    
    path('Admin-Remove/<int:pk>',views.admin_remove,name="admin_remove"),
    path('View-Register/<int:pk>',views.view_details,name="view_details"),
    path('Approve-Payment/<int:pk>',views.admin_approve,name="admin_approve"),
    path('Confirm-Payment/<int:pk>',views.admin_confirm,name="admin_confirm"),
    
    
    
    
    
    
    
    ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)