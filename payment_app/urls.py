from django.urls import path 
from.import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

    path('',views.login_page,name='login_page'),
    path('Login-Dashboard',views.login_dashboard,name='login_dashboard'),
    path('Admin-Dashboard',views.admin_dashboard,name='admin_dashboard'),

    #account
    
    path('Account-Profile',views.account_profile,name='account_profile'),
    path('Account-Password-Change',views.account_password_change,name='account_password_change'),
    


    path('Account-Dashboard',views.dashboard,name='dashboard'),
    path('All-Payments',views.allpayments,name='allpayments'),
    path('Pending-Payments',views.pending_payments,name='pending_payments'),
    path('Completed-Payments',views.completed_payments,name='completed_payments'),
    path('Incompleted-Payments',views.incompleted_payments,name='incompleted_payments'),
    path('Next-Payments',views.track_payments,name='track_payments'),
    path('Upcoming-Payments',views.upcoming_payments_list,name='upcoming_payments_list'),
    path('Quick-Search/<int:pk>',views.quick_search,name="quick_search"),
    path('Payments-Search',views.paysearch,name='paysearch'),

    # Account Section 
    path('Account',views.accounts,name='accounts'),
    path('Fixed-Expence',views.fixed_expence,name='fixed_expence'),
    path('Fixed-Expence-Save',views.fixed_expence_add,name='fixed_expence_add'),
    path('Fixed-Edit/<int:pk>',views.fixed_edit,name="fixed_edit"),
    path('Fixed-Delete/<int:pk>',views.fixed_delete,name="fixed_delete"),
    path('Fixed-Status-Change/<int:pk>',views.fixed_change_status,name="fixed_change_status"),

    path('Company-Holoidays',views.company_holoidays,name='company_holoidays'),
    path('Company-Holoidays-Add',views.company_holiday_add,name='company_holiday_add'),
    path('Company-Holoidays-Edit/<int:pk>',views.company_holidy_edit,name="company_holidy_edit"),
    
    
    
    
    
    
    path('Salary-Expence',views.salary_expence,name='salary_expence'),
    path('Income-Expence',views.income_expence_form,name='income_expence_form'),
    path('Income-Expence-Save',views.income_expence_add,name='income_expence_add'),
    
    
    path('Employee-Register-Form',views.emp_Register_form,name='emp_Register_form'),
    path('Employee-Register',views.employee_register_Details,name='employee_register_Details'),
    path('Employee-Register-Search',views.register_search,name='register_search'),

    path('Employee-Deactive/<int:pk>',views.emp_reg_deactive,name="emp_reg_deactive"),
    path('Employee-Active/<int:pk>',views.emp_reg_reactive,name="emp_reg_reactive"),
    path('Employee-Salary-Active/<int:pk>',views.emp_salary_active,name="emp_salary_active"),
    path('Employee-Salary-Deactive/<int:pk>',views.emp_salary_deactive,name="emp_salary_deactive"),
    path('Employee-Delete/<int:pk>',views.emp_reg_delete,name="emp_reg_delete"),
    
    
    
    
    
    #path('Remainig-Salary-Payment',views.remaining_salary_expence,name='remaining_salary_expence'),
    path('All-Salary-Expence',views.all_salary_expence,name='all_salary_expence'),
    path('Salary-Expence-Search',views.Search_salary_payments,name='Search_salary_payments'),
    
    path('Salary-Expence-Form',views.salary_expence_form,name='salary_expence_form'),
    path('Salary-Expence-Add/<int:pk>',views.salary_expence_add,name="salary_expence_add"),
    path('Salary-Expence-Save',views.employee_salary_save,name='employee_salary_save'),
    path('Salary-Expence-Calculate',views.salary_calculate,name='salary_calculate'),
    
    
    path('Employee-Salary-Details/<int:pk>',views.employee_salary_details,name="employee_salary_details"),
    path('Employee-Salary-Details-Search/<int:pk>',views.employee_salary_payments_search,name="employee_salary_payments_search"),
    

    
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
    
    path('Admin-Profile',views.admin_account,name='admin_account'),
    path('Admin-Password-Save',views.admin_password_changeing,name='admin_password_changeing'),
    

    path('New-Payments-List',views.newpay_confirm_list,name='newpay_confirm_list'),
    path('Payment-Track',views.admin_trackPayments,name='admin_trackPayments'),
    path('Admin-Upcoming-Payments',views.adminupcomingPayments,name='adminupcomingPayments'),
    path('Admin-Payments-View',views.admin_paymentsview,name='admin_paymentsview'),
    path('Admin-Payments-FullView',views.adminpaymentfull_view,name='adminpaymentfull_view'),
    path('Admin-Payments-Search',views.adminsearch_data_full,name='adminsearch_data_full'),
    
    
    path('Admin-User-List',views.admin_user_list,name='admin_user_list'),
    path('Admin-All-User-Payments',views.admin_allpayments_list,name='admin_allpayments_list'),
    path('Admin-Pending-Payments',views.admin_pending_payments,name='admin_pending_payments'),
    path('Admin-Completed-Payments',views.admin_completed_payments,name='admin_completed_payments'),
    path('Admin-Incompleted-Payments',views.admin_incompleted_payments,name='admin_incompleted_payments'),
    path('Admin-Payment-Search',views.adminpaysearch,name='adminpaysearch'),
    
    path('Admin-Quick-Search/<int:pk>',views.adminquick_search,name="adminquick_search"),
    
    
    
    path('Admin-Remove/<int:pk>',views.admin_remove,name="admin_remove"),
    path('View-Register/<int:pk>',views.view_details,name="view_details"),
    path('Approve-Payment/<int:pk>',views.admin_approve,name="admin_approve"),
    path('Confirm-Payment/<int:pk>',views.admin_confirm,name="admin_confirm"),


# Admin Accounts Section 

    path('Admin-Accounts',views.admin_accounts,name='admin_accounts'),
    path('Admin-Employee-View',views.admin_emp_Register_view,name='admin_emp_Register_view'),
    path('Admin-Employee-Search',views.admin_register_search,name='admin_register_search'),
    path('Admin-Income-Expence',views.admin_income_expence,name='admin_income_expence'),
    path('Admin-Income-Expence-Add',views.admin_income_expence_add,name='admin_income_expence_add'),
    
    path('Admin-Income-Expence-Search',views.admin_income_expence_search,name='admin_income_expence_search'),
    path('Admin-Salary-Expence',views.admin_salary_expence,name='admin_salary_expence'),
    path('Admin-AllSalary-Expence',views.admin_all_salary_expence,name='admin_all_salary_expence'),
    path('Admin-AllSalary-Expence-Search',views.admin_search_salary_payments,name='admin_search_salary_payments'),
    
    path('Admin-Employee-Salary_Details/<int:pk>',views.admin_employee_salary_details,name="admin_employee_salary_details"),
    path('Admin-Employee-Salary-Payments-Search/<int:pk>',views.admin_employee_salary_payments_search,name="admin_employee_salary_payments_search"),

    path('Admin-Employee-Reg-deactive/<int:pk>',views.admin_emp_reg_deactive,name="admin_emp_reg_deactive"),
    path('Admin-Employee-Reg-active/<int:pk>',views.admin_emp_reg_reactive,name="admin_emp_reg_reactive"),
    path('Admin-Employee-Salary-active/<int:pk>',views.admin_emp_salary_active,name="admin_emp_salary_active"),
    path('Admin-Employee-Salary-deactive/<int:pk>',views.admin_emp_salary_deactive,name="admin_emp_salary_deactive"),
    path('Admin-Employee-Reg-delete/<int:pk>',views.admin_emp_reg_delete,name="admin_emp_reg_delete"),
    path('Admin-Fixed-Expence',views.admin_fixed_expence,name='admin_fixed_expence'),
    path('Admin-Fixed-Expence-Add',views.admin_fixed_expence_add,name='admin_fixed_expence_add'),
    path('Admin-Fixed-Edit/<int:pk>',views.admin_fixed_edit,name="admin_fixed_edit"),
    path('Admin-Fixed-Status/<int:pk>',views.admin_fixed_change_status,name="admin_fixed_change_status"),
    path('Admin-Fixed-Delete/<int:pk>',views.admin_fixed_delete,name="admin_fixed_delete"),

    path('Admin-Holidays',views.admin_company_holoidays,name='admin_company_holoidays'),
    path('Admin-Holiday-Add',views.admin_company_holiday_add,name='admin_company_holiday_add'),
    path('Admin-Holiday-Edit/<int:pk>',views.admin_company_holidy_edit,name="admin_company_holidy_edit"),


    # Admin Analysis section 
    
    path('Admin-Analysis',views.admin_analysis,name='admin_analysis'),
    



    
    
    
    
    
    
    
    
    
    
    path('LogOut',views.logout_page,name='logout_page'),
    
    
    
    
    ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)