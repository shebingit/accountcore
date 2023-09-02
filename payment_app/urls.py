from django.urls import path 
from.import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

 
   
    path('',views.login_page,name='login_page'),
    path('Login-Dashboard',views.login_dashboard,name='login_dashboard'),
    path('Admin-Dashboard',views.admin_dashboard,name='admin_dashboard'),

    #========================== Account Section ======================================

    #Account management------------
    path('Account-Profile',views.account_profile,name='account_profile'),
    path('Account-Profile-Save',views.profile_account_details_save,name='profile_account_details_save'),
    path('Account-Password-Change',views.account_password_change,name='account_password_change'),

    #---------------------- Main section ---------------- 
    path('Account-Dashboard',views.dashboard,name='dashboard'),
    path('Account-OJT-List',views.OJT_list_view,name='OJT_list_view'),
    path('Account-Employee-List',views.employee_list_view,name='employee_list_view'),
    path('Allocate-List/<int:pk>',views.allocate_list,name='allocate_list'),
    

    #----------------------Sidebar section --------------

    #Register links-----------
    path('Register-Form',views.Register_form,name='Register_form'),
    path('Employee-Register-Form',views.emp_Register_form,name='emp_Register_form'),
    path('Department-Form',views.department_form,name='department_form'),

    #Payment view -----------
    path('Payments-List',views.pyments_history,name='pyments_history'),
    path('Payments-Status/<int:pk>',views.pyments_status_view,name='pyments_status_view'),
   
    

    #----------------------OJT Payment------------------
    path('Payment-Add-Form',views.pyment_form,name='pyment_form'),
    path('Add-Pay-Details/<int:pk>',views.addpayment_details,name="addpayment_details"),
    path('Pay-List',views.ojt_payment_list_single,name="ojt_payment_list_single"),
    path('OJT-Payment-Edit',views.ojt_payment_edit,name="ojt_payment_edit"),
    
    
    
   

    
    
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
    path('Fixed-Edit/<int:pk>',views.fixed_edit,name="fixed_edit"),
    path('Fixed-Delete/<int:pk>',views.fixed_delete,name="fixed_delete"),
    path('Fixed-Status-Change/<int:pk>',views.fixed_change_status,name="fixed_change_status"),

    path('Company-Holoidays',views.company_holoidays,name='company_holoidays'),
    path('Company-Holoidays-Edit/<int:pk>',views.company_holidy_edit,name="company_holidy_edit"),
    
    
    path('Recipt-Data',views.recipt_data,name='recipt_data'),
    path('Recipt-Data-Save',views.recipt_data_save,name='recipt_data_save'),
    
    
    
    
    path('Salary-Expence',views.salary_expence,name='salary_expence'),
    path('Income-Expence',views.income_expence_form,name='income_expence_form'),
    
    path('Income-Expence-Search',views.income_expence_search,name='income_expence_search'),
    path('Income-Expence-Edit/<int:inex_edit>',views.income_expence_edit,name="income_expence_edit"),
    path('Income-Expence-Delete/<int:incom_delete>',views.income_expence_delete,name="income_expence_delete"),
    
    
    path('Employee-Register',views.emp_Register_form,name='emp_Register_form'),
    path('Employee-Register',views.employee_register_Details,name='employee_register_Details'),
    path('Employee-Register-Search',views.register_search,name='register_search'),
    path('Employee-Edit/<int:pk>',views.employee_reg_edit,name="employee_reg_edit"),
    path('Employee-Edit-Save/<int:pk>',views.employee_register_Details_edit,name="employee_register_Details_edit"),

    path('Employee-Deactive/<int:pk>',views.emp_reg_deactive,name="emp_reg_deactive"),
    path('Employee-Active/<int:pk>',views.emp_reg_reactive,name="emp_reg_reactive"),
    path('Employee-Salary-Active/<int:pk>',views.emp_salary_active,name="emp_salary_active"),
    path('Employee-Salary-Deactive/<int:pk>',views.emp_salary_deactive,name="emp_salary_deactive"),
    path('Employee-Delete/<int:pk>',views.emp_reg_delete,name="emp_reg_delete"),
    
    
    
    
    
    #path('Remainig-Salary-Payment',views.remaining_salary_expence,name='remaining_salary_expence'),
    path('All-Salary-Expence',views.all_salary_expence,name='all_salary_expence'),
    path('Salary-Expence-Search',views.Search_salary_payments,name='Search_salary_payments'),
    
    path('Salary-Expence-Form',views.salary_expence_form,name='salary_expence_form'),
    path('Salary-Pending',views.employee_pending_salary,name='employee_pending_salary'),
    
    path('Salary-Expence-Add/<int:pk>',views.salary_expence_add,name="salary_expence_add"),
    path('Salary-Expence-Edit/<int:pk>',views.salary_expence_edit,name="salary_expence_edit"),
    path('Salary-Expence-Edit-Save',views.salary_edit_save,name="salary_edit_save"),
    
    
    path('Salary-Expence-Save',views.employee_salary_save,name='employee_salary_save'),
    path('Salary-Expence-Calculate',views.salary_calculate,name='salary_calculate'),
    
    
    path('Employee-Salary-Details/<int:pk>',views.employee_salary_details,name="employee_salary_details"),
   
    

    
    path('Users-List',views.Users_list,name='Users_list'),
    path('Edit-User/<int:pk>',views.edit_user,name="edit_user"),
    path('Edit-User-Details/<int:pk>',views.edit_Details,name="edit_Details"),
    path('Edit-Register-User/<int:pk>',views.register_edit,name="register_edit"),
   
    
    
    
    
   
    path('Pay-Details/<int:pk>',views.payment_details,name="payment_details"),
 
    path('Pay-Details-Remove/<int:pk>',views.payhis_remove,name="payhis_remove"),
    

    #Search Data based on Date
    
    path('Search',views.Search_data,name='Search_data'),
    path('Search-Full',views.Search_data_full,name='Search_data_full'),
     
    
    
    path('Department-Form',views.department_form,name='department_form'),
    path('Edit-Department/<int:pk>',views.edit_dept,name="edit_dept"),
    path('Remove-Department/<int:pk>',views.remove_dept,name="remove_dept"),

    # Payments History section
    
    path('PaymentsView-List',views.paymentfull_view,name='paymentfull_view'),
    
    path('User-Payments-Details/<int:pk>',views.singleuser_details,name="singleuser_details"),
    path('Previous-Details/<int:pk>',views.previous_data,name="previous_data"),
    path('Next-Payments-Details/<int:pk>',views.next_data,name="next_data"),
    
   
    path('Deactive-Reactive-User/<int:pk>',views.user_active_reactive,name="user_active_reactive"),
    path('Delete-User/<int:pk>',views.delete_user,name="delete_user"),
    
    
    #Receipt Sigle data 
    path('Payment-Recipt/<int:pk>',views.singeldata_receipt,name="singeldata_receipt"),
    path('Full-Payment-Recipt/<int:pk>',views.singelUserfull_receipt,name="singelUserfull_receipt"),
    

    #path('Confirm/<int:pk>',views.confirm,name="confirm"),
    path('Remove/<int:pk>',views.remove,name="remove"),
    #path('Payment-Completed/<int:pk>',views.payment_completed,name="payment_completed"),


    # Analyis section 
    path('Analysis',views.analysis,name='analysis'),
    path('Analysis-on-Month',views.analysis_months,name='analysis_months'),
    path('Analysis-Search',views.analysis_search,name='analysis_search'),
    
    
    
    
    

    #========================== Admin ==============================================
    
    path('Admin-Profile',views.admin_account,name='admin_account'),
    path('Admin-Profile-Details-Save',views.admin_account_details_save,name='admin_account_details_save'),
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
    
    
    path('Admin-Department-Form',views.admin_department_form,name='admin_department_form'),
    path('Admin-Add-Department',views.admin_department_add,name='admin_department_add'),
    path('Admin-Edit-Department/<int:pk>',views.admin_edit_dept,name="admin_edit_dept"),
    path('Admin-Remove-Department/<int:pk>',views.admin_remove_dept,name="admin_remove_dept"),
    
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
    
    #----------------Company Analysis----------------------
    path('Admin-Analysis',views.admin_analysis,name='admin_analysis'),
    path('Admin-Analysis-On_Months',views.admin_analysis_months,name='admin_analysis_months'),
    path('Admin-Analysis-On_Months-Search',views.admin_analysis_search,name='admin_analysis_search'),
    path('Company-Income-Expence-analysis',views.admin_analysis_income_expence_details,name='admin_analysis_income_expence_details'),
    path('Analysis-OJT',views.admin_analysis_OJT_details,name='admin_analysis_OJT_details'),
    path('OJT-Payments-Details/<int:pk>',views.admin_registartion_ojt_payment_details,name="admin_registartion_ojt_payment_details"),
    path('Analysis-OJT-All-Registration',views.admin_ojt_registration_all_states,name='admin_ojt_registration_all_states'),
    path('Analysis-OJT-Upcoming-Payments',views.admin_ojt_current_upcoming_payments,name='admin_ojt_current_upcoming_payments'),
    path('Analysis-OJT-Analyis-Payments-Status',views.admin_ojt_analysis_payment_status,name='admin_ojt_analysis_payment_status'),
    path('Analysis-Employee',views.admin_analysis_employee_details,name='admin_analysis_employee_details'),
    path('Analysis-All-Employee',views.admin_employee_analyis_registration_all_states,name='admin_employee_analyis_registration_all_states'),
    path('Analysis-Employee-Paid-Salary',views.admin_emp_salary_paid_list,name='admin_emp_salary_paid_list'),
    path('Analysis-UnPaid-Salary',views.admin_emp_salary_unpaid_list,name='admin_emp_salary_unpaid_list'),
    path('Analysis-Deactive-Salary-Account',views.admin_emp_deactive_salary_account_list,name='admin_emp_deactive_salary_account_list'),
    path('Analysis-EmployeeSalary-Payments-Details/<int:emp_id>',views.admin_emp_salary_pay_details,name='admin_emp_salary_pay_details'),

   



    path('Admin-State-Assign',views.admin_state_form,name='admin_state_form'),
    path('Admin-Employee-Register-Form',views.admin_employee_register_form,name='admin_employee_register_form'),
    path('Admin-Employee-Register',views.admin_employee_register,name='admin_employee_register'),
    path('Admin-State-Register',views.admin_state_register,name='admin_state_register'),
    path('Admin-State-Allocation',views.admin_state_allocation,name='admin_state_allocation'),
    path('Admin-State-Re-allocation',views.admin_state_reallocation,name='admin_state_reallocation'),

    
    path('LogOut',views.logout_page,name='logout_page'),
    
    
    
    
    ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)