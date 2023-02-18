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
    path('Payment-Add',views.pyment_form,name='pyment_form'),
    path('Add-Pay-Details/<int:pk>',views.addpayment_details,name="addpayment_details"),
    path('Pay-Details/<int:pk>',views.payment_details,name="payment_details"),
    path('Payment-Save',views.save_payment,name='save_payment'),
    
    
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

    

    

    path('Register-Form',views.Register_form,name='Register_form'),
    path('Register-Save',views.register_Details,name='register_Details'),
    #path('Confirm/<int:pk>',views.confirm,name="confirm"),
    path('Remove/<int:pk>',views.remove,name="remove"),
    #path('Payment-Completed/<int:pk>',views.payment_completed,name="payment_completed"),
    
    

    #admin 
    path('New-Payments-List',views.newpay_confirm_list,name='newpay_confirm_list'),
    path('Admin-Remove/<int:pk>',views.admin_remove,name="admin_remove"),
    path('View-Register/<int:pk>',views.view_details,name="view_details"),
    path('Approve-Payment/<int:pk>',views.admin_approve,name="admin_approve"),
    path('Confirm-Payment/<int:pk>',views.admin_confirm,name="admin_confirm"),
    
    
    
    
    
    
    ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)