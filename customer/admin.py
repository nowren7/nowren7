from django.contrib import admin
from . models import CustomerDetails, FinesDetails, SalikDetails, VehicleDetails,ExcelFile,UserSaving

class CustomerDetailsDash(admin.ModelAdmin):
    fieldsets =\
        (
        ("Personal Details",{
            "fields":("name","email","phonenumber","Dob","nationality"),}),
        ("Other Details",{"fields":("documentID","driver_license_number","driver_country_of_issue","driver_date_of_issue",
                                    "driver_date_of_expiry","emirates_id_passport_number",
                                    "emirates_id_passport_date_of_issue","emirates_id_passport_date_of_expiry"),}),
        )
    list_display = ('name','documentID','driver_license_number')


# Register your models here.
admin.site.register(VehicleDetails)
admin.site.register(ExcelFile)
admin.site.register(CustomerDetails,CustomerDetailsDash)
admin.site.register(SalikDetails)
admin.site.register(FinesDetails)
admin.site.register(UserSaving)