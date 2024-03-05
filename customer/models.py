from datetime import timedelta
from django.db import models

class VehicleDetails(models.Model):
    STATUS_CHOICES = [
        ('Not started', 'Not started'),
        ('Pending', 'Pending'),
        ('Under process', 'Under process'),
        ('Upload Done', 'Upload Done'),
        ('Contract Closed', 'Contract Closed'),
    ]

    UserId = models.IntegerField() 
    Vehicle_No=models.CharField(max_length=200)
    Ride_distance = models.FloatField()
    Start_date = models.DateTimeField(null=False, blank=True)  # Use DateTimeField instead of DateField
    End_date = models.DateTimeField(null=False, blank=True) 
    Ride_duration = models.DurationField()
    Total_cost = models.DecimalField(max_digits=10, decimal_places=5)
    Add_Date = models.DateTimeField(auto_now=True)
    Ride_ID = models.CharField(max_length=60)
    User_PhoneNo = models.CharField(max_length=100)
    Status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='')
    VehiclemodelID = models.CharField(max_length=100)
    Vehiclestartlatitude = models.CharField(max_length=100)
    Vehiclestartlongitude = models.CharField(max_length=100)
    Vehicleendlatitude = models.CharField(max_length=100)
    Vehicleendlongitude = models.CharField(max_length=100)
    Userphonenumber = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return str(self.UserId)


class ExcelFile(models.Model):
    file = models.FileField(upload_to='uploads/')


class CustomerDetails(models.Model):
    ID=models.IntegerField()
    name=models.CharField(max_length=200)
    email = models.EmailField(max_length=100)
    phonenumber=models.CharField(max_length=30)
    documentID=models.CharField(max_length=30)

    class Meta:
        verbose_name = 'customer'
        verbose_name_plural = 'customer'
    def __str__(self):
         return str(self.ID)
    
class SalikDetails(models.Model):
    STATUS_CHOICES = [
        ('Not started', 'Not started'),
        ('Pending', 'Pending'),
        ('Invoiced', 'Invoiced'),
        ('Partial Paid', 'Partial Paid'),
        ('Paid', 'Paid'),
    ]

    TarnsactionID=models.CharField(max_length=100)
    TripDate= models.DateField(null=False, blank=True)
    TripTime = models.TimeField(null=True, blank=True)  
    Plate=models.CharField(max_length=30)
    Amount=models.CharField(max_length=30)
    Ride_ID = models.CharField(max_length=60, null=True, blank=True)
    UserId = models.IntegerField(null=True, blank=True)
    Status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='')

    class Meta:
        verbose_name = 'Salik'
        verbose_name_plural = 'Salik'
    def __str__(self):
        return self.TarnsactionID
    
class FinesDetails(models.Model):
    STATUS_CHOICES = [
        ('Not started', 'Not started'),
        ('Pending', 'Pending'),
        ('Invoiced', 'Invoiced'),
        ('Partial Paid', 'Partial Paid'),
        ('Paid', 'Paid'),
    ]

    PlateNo = models.CharField(max_length=100)
    PlateCode = models.CharField(max_length=100)
    PlateCategory = models.CharField(max_length=100)
    LicenseNo = models.CharField(max_length=100)
    LicenseFrom = models.CharField(max_length=100)
    TicketNo = models.CharField(max_length=100)
    TicketDate = models.DateField(null=False, blank=True)
    TicketTime = models.TimeField()
    FinesSource = models.CharField(max_length=100)
    TicketFee = models.CharField(max_length=100)
    TicketStatus = models.CharField(max_length=100)
    TermsoftheOffense = models.CharField(max_length=100)
    Ride_ID = models.CharField(max_length=60, null=True, blank=True)
    Status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='')

    class Meta:
        verbose_name = 'Fines'
        verbose_name_plural = 'Fines'
    def __str__(self):
        return self.PlateNo
    
class UserSaving(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    password = models.CharField(max_length=100, default='')
    
    class Meta:
        verbose_name = 'Users'
        verbose_name_plural = 'Users'
    def __str__(self):
        return self.name
    




    

        
