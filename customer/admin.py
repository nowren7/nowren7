from django.contrib import admin
from . models import CustomerDetails, FinesDetails, SalikDetails, VehicleDetails,ExcelFile,UserSaving
# Register your models here.
admin.site.register(VehicleDetails)
admin.site.register(ExcelFile)
admin.site.register(CustomerDetails)
admin.site.register(SalikDetails)
admin.site.register(FinesDetails)
admin.site.register(UserSaving)