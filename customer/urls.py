from django.urls import path
from django.contrib import admin
from customer import views
# can you cal in botim

urlpatterns = [
    path('index',views.index,name="index"),
    path('ExcelUpload',views.ExcelUpload,name="tables"),
    path('exceltable', views.upload_file_update, name="excel_table"),
    path('ppmcontract', views.rentalcontract,name="rentalcontracts"),
    path('contractpdf',views.merge_data,name="contractpdf"),
    path('download_form',views.download_form, name="download_form"),
    path('sumsub/<str:document_id>/',views.SumSubAPI,name="sumsub"),
    path('submit-form/', views.form_submit, name='form_submit'),
    path('exceltablecustomer',views.customer_upload,name="customerupload"),
    path('salikurl',views.salik_Finance,name="salik"),
    path('finesurl',views.fines_excel,name="fines"),
    path('',views.login_page,name="login"),
    path('users', views.users_adding, name='users_adding'),
    path('delete_user/<int:id>/', views.delete_user, name='delete_user'),
    path('edit_user/<int:id>/', views.edit_user, name='edit_user'),
    path('update_status', views.update_status, name='update_status'),
    

    # path('display_user_table/', views.get_user_data, name='display_user_table'),
]
  




