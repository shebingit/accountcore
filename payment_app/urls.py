from django.urls import path 
from.import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

    path('',views.login,name='login'),
    path('Account-Dashboard',views.dashboard,name='dashboard'),
    path('Department-Form',views.department_form,name='department_form'),
    path('Add-Department',views.department_add,name='department_add'),
    path('Remove-Department/<int:pk>',views.remove_dept,name="remove_dept"),
    

    path('Register-Form',views.Register_form,name='Register_form'),
    path('Register-Save',views.register_Details,name='register_Details'),
    path('Confirm/<int:pk>',views.confirm,name="confirm"),
    path('Remove/<int:pk>',views.remove,name="remove"),
    
    
    ]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)