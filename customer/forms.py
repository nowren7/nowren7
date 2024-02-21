from django import forms
from .models import UserSaving, VehicleDetails, CustomerDetails


#vehicle excel upload
class ExcelUploadForm(forms.Form):
    file = forms.FileField()

#vehicle excel details getting
class VehicleForm(forms.ModelForm):
     class Meta:
        model = VehicleDetails
        fields = '__all__'

#customer excel upload
class CustomerExcelForm(forms.Form):
    file = forms.FileField()

#customer excel details getting        
class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerDetails
        fields = '__all__'

#salik excel upload
class SalikExcelForm(forms.Form):
    file = forms.FileField()

#fines excel upload
class FinesExcelForm(forms.Form):
    file = forms.FileField()

#usersaving form
class UserSavingForm(forms.ModelForm):
    class Meta:
        model = UserSaving
        fields = '__all__'

