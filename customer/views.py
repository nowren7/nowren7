from email.utils import parsedate
import hashlib
import hmac
import time
from venv import create
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.http import  HttpResponse, JsonResponse
from psycopg2 import IntegrityError
from .forms import CustomerExcelForm, FinesExcelForm, SalikExcelForm, UserSavingForm, VehicleForm, ExcelUploadForm,CustomerForm
from django.shortcuts import render
import pandas as pd
from .models import CustomerDetails, FinesDetails, SalikDetails, UserSaving, VehicleDetails
import json
import requests
from datetime import datetime, timedelta
from decimal import Decimal
from .utils import sign_request, REQUEST_TIMEOUT
from django.utils.dateparse import parse_time,parse_date
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import datetime
# ----------------------------------------------------------------------------------------------


def login_page(request):
    username = request.GET.get('uservalue')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = UserSaving.objects.get(name=username, password=password)
            request.session['useraccess']=username
            return redirect('index')  # Replace 'index' with the appropriate URL name for the user page
        except UserSaving.DoesNotExist:
            request.session['useraccess']=None
            messages.error(request, 'Invalid username or password. Please try again.')
            return redirect('login')  # Redirect back to the login page with an error message
    return render(request, 'Login.html')


# Welcome page
def index(request):
    print(request.session.get('useraccess'))
    if request.session.get('useraccess'):
        return render(request,'index.html')
    else:
        return redirect('login')
# customer page vehicle upload
def ExcelUpload(request):
    from .forms import ExcelUploadForm,CustomerExcelForm
    form = ExcelUploadForm()
    form = CustomerExcelForm()
    return render(request,'format.html',{'form':form})




# vehicle individual upload to format
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


import datetime  # Import the datetime module

def upload_file_update(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_files = form.cleaned_data['file']
            df = pd.read_excel(excel_files)

            vehicle_data = []

            for index, row in df.iterrows():
                ride_duration_str = str(row['Ride duration'])
                start_date_str = str(row['Start date'])
                end_date_str = str(row['End date'])
                try:
                    start_date = datetime.datetime.strptime(start_date_str, "%d/%m/%Y %H:%M:%S")  # Use datetime.datetime.strptime()
                    end_date = datetime.datetime.strptime(end_date_str, "%d/%m/%Y %H:%M:%S")  # Use datetime.datetime.strptime()
                except ValueError:
                    start_date = None
                    end_date = None
                
                user_id = row['User ID']
                if user_id != '-':
                    try:
                        user_id = int(user_id)
                    except ValueError:
                        user_id = None

                    try:
                        vehicle_instance = VehicleDetails.objects.get(UserId=user_id)
                        # Update existing instance
                        vehicle_instance.Ride_ID = row['ID']
                        vehicle_instance.Vehicle_No = row['Vehicle No.']
                        vehicle_instance.Ride_distance = row['Ride distance (km)']
                        vehicle_instance.Start_date = start_date
                        vehicle_instance.End_date = end_date
                        vehicle_instance.Ride_duration = ride_duration_str
                        vehicle_instance.Total_cost = round(Decimal(row['Total cost (AED)']), 2)
                        vehicle_instance.User_PhoneNo = row['User phone number']
                        vehicle_instance.VehiclemodelID = row['Vehicle model ID']
                        vehicle_instance.Vehiclestartlatitude = row['Vehicle start latitude']
                        vehicle_instance.Vehiclestartlongitude = row['Vehicle start longitude']
                        vehicle_instance.Vehicleendlatitude = row['Vehicle end latitude']
                        vehicle_instance.Vehicleendlongitude = row['Vehicle end longitude']
                        
                        # vehicle_instance.Status = request.POST.get(f"status_{id}")  # Save status from dropdown
                        vehicle_instance.save()
                    except VehicleDetails.DoesNotExist:
                        # Create new instance
                        instance = VehicleDetails(
                            Ride_ID=row['ID'],
                            Vehicle_No=row['Vehicle No.'],  # Use Excel column name
                            Ride_distance=row['Ride distance (km)'],  # Use Excel column name
                            Start_date=start_date,
                            End_date=end_date,
                            Ride_duration=ride_duration_str,
                            Total_cost=Decimal(row['Total cost (AED)']),  # Use Excel column name
                            UserId=user_id,  # Use Excel column name
                            User_PhoneNo=row['User phone number'],
                            VehiclemodelID = row['Vehicle model ID'],
                            Vehiclestartlatitude = row['Vehicle start latitude'],
                            Vehiclestartlongitude = row['Vehicle start longitude'],
                            Vehicleendlatitude = row['Vehicle end latitude'],
                            Vehicleendlongitude = row['Vehicle end longitude']
                        
                            # Status=request.POST.get(f"status_{id}")  # Save status from dropdown
                        )
                        instance.save()

                    vehicle_data.append({
                        'Ride_ID': row['ID'],
                        'Vehicle_No': row['Vehicle No.'],  # Use Excel column name
                        'Ride_distance': row['Ride distance (km)'],  # Use Excel column name
                        'Start_date': start_date_str,
                        'End_date': end_date_str,
                        'Ride_duration': ride_duration_str,
                        'Total_cost': round(Decimal(row['Total cost (AED)']), 2),  # Use Excel column name
                        'UserId': user_id,  # Use Excel column name
                        'User_PhoneNo': row['User phone number']
                        # 'Status': request.POST.get(f"status_{id}")  # Add status to vehicle_data
                    })

            # Returning JsonResponse with the updated data
            return render(request, 'tables.html', {'form': form, 'vehicle_data': vehicle_data})
    else:
        existing_data = VehicleDetails.objects.order_by('-Ride_ID').values()

        paginator = Paginator(existing_data, 50)  # Show 50 items per page

        page_number = request.GET.get('page')
        try:
            vehicle_data = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            vehicle_data = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            vehicle_data = paginator.page(paginator.num_pages)

        # Debugging line
        form = ExcelUploadForm()
        return render(request, 'tables.html', {'form': form, 'vehicle_data': vehicle_data})





#Get sumsub customer details
def GetUserSum(applicantId):
    SUMSUB_TEST_BASE_URL = "https://api.sumsub.com"
    # id='3496288-2151128'
    # https://api.sumsub.com/resources/applicants/-;externalUserId=3495717-2151064/one
    url = SUMSUB_TEST_BASE_URL + f'/resources/applicants/{applicantId}/one'
    resp = sign_request(requests.Request('GET', url))
    s = requests.Session()
    response = s.send(resp, timeout=REQUEST_TIMEOUT)
    try:
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        data = json.loads(response.text)
        return data

    except requests.exceptions.RequestException as e:
        # Handle API request errors here
        return {'error': str(e)}
    # response_data = json.loads(response.text)
    # print(response_data)
    # return render(request,'sumsub.html',{'data':response_data})


def SumSubAPI(request, document_id):
    data = GetUserSum(document_id)
    return render(request, 'sumsub.html', {'data': data})

#merged vehicle and customer table
def contractpdf(request):
    # print("rental")
    return render(request,"contractpdf.html")

#contract form page
def rentalcontract(request):
    from .forms import VehicleForm
    form = VehicleForm()
    return render(request, 'ppmcontract.html', {'form': form})
  


# contract form values getting
def download_form(request):
    from .forms import VehicleForm
    from . models import CustomerDetails
    vehicle_no = request.GET.get('Vehicle_No')
    ride_distance = request.GET.get('Ride_distance')
    start_date = request.GET.get('Start_date')
    end_date = request.GET.get('End_date')
    ride_duration = request.GET.get('Ride_duration')
    total_cost = request.GET.get('Total_cost')
    userid = request.GET.get('UserId')
    rideid = request.GET.get('Ride_ID')
    userphone = request.GET.get('User_PhoneNo')
    
    # customer_id = CustomerDetails.objects.get(ID=userid)
    # customer_phone_number = customer_id.phonenumber
    # # form.fields['Vehicle_No'].initial = vehicle_no
    initial_values = {
        'Vehicle_No': vehicle_no,
        'Ride_distance': ride_distance,
        'Start_date': start_date,
        'End_date': end_date,
        'Ride_duration': ride_duration,
        'Total_cost': total_cost,
        'UserId': userid,
        'Ride_ID':rideid,
        # 'PhoneNumber': customer_phone_number,
        'User_PhoneNo': userphone
    }
    # Pass the initial values to the form
    form = VehicleForm(initial=initial_values)

    report = f"Vehicle No: {vehicle_no}\n" \
             f"Ride Distance: {ride_distance}\n" \
             f"Start Date: {start_date}\n" \
             f"End Date: {end_date}\n" \
             f"Ride Duration: {ride_duration}\n" \
             f"Total Cost: {total_cost}\n" \
             f"User ID: {userid}\n" \
             f"ID:{rideid}\n" \
             f"User phone number:{userphone}\n" \
             
             
    # print(customer_phone_number)
    try:
        customer_id = CustomerDetails.objects.get(Customer_ID=userid)
    except CustomerDetails.DoesNotExist:
        messages.error(request,"Customer Does not exist")
        return render(request,'ppmcontract.html')
    
    
    

    # print(customer_id.documentID)
    customer_sumsub=customer_id.documentID
    SUMSUB_TEST_BASE_URL = "https://api.sumsub.com"
    id=customer_sumsub
    # url = "https://api.sumsub.com/resources/applicants/64d292ff68f04c0d4adcfd56/one"
    # https://api.sumsub.com/resources/applicants/-;externalUserId=3495717-2151064/one
    # url = SUMSUB_TEST_BASE_URL + f'/resources/applicants/-;externalUserId={id}/one'
    url = SUMSUB_TEST_BASE_URL + f'/resources/applicants/{id}/one'
    resp = sign_request(requests.Request('GET', url))
    s = requests.Session()
    response = s.send(resp, timeout=REQUEST_TIMEOUT)
    response_data = json.loads(response.text)

    customer_name = response_data.get('info', {}).get('firstName', '')
    customer_Dob = response_data.get('info', {}).get('dob', '')
    # customer_mobile = response_data.get('info',[{}]).get('')
    customer_nationality = response_data.get('info',{}).get('nationality','')
    # Initialize variables
    driver_license_number = ''
    driver_country_of_issue = ''
    driver_date_of_issue = ''
    driver_date_of_expiry = ''
    emirates_id_passport_number = ''
    emirates_id_passport_date_of_issue = ''
    emirates_id_passport_date_of_expiry = ''

    # Iterate through idDocs
    for id_doc in response_data.get('info', {}).get('idDocs', []):
        doc_type = id_doc.get('idDocType', '')
        if doc_type == 'DRIVERS':
        # Driver’s License
            driver_license_number = id_doc.get('number', '')
            driver_country_of_issue = id_doc.get('country', '')
            driver_date_of_issue = id_doc.get('issuedDate', '')
            driver_date_of_expiry = id_doc.get('validUntil', '')
        elif doc_type in ['RESIDENCE_PERMIT', 'ID_CARD']:
        # Emirates ID/Passport
            emirates_id_passport_number = id_doc.get('additionalNumber', '')
            emirates_id_passport_date_of_issue = id_doc.get('issuedDate', '')
            emirates_id_passport_date_of_expiry = id_doc.get('validUntil', '')
    try:
        print(customer_id)
        customer_id.name = customer_name
        customer_id.Dob = customer_Dob
        customer_id.nationality = customer_nationality
        customer_id.driver_license_number = driver_license_number
        customer_id.driver_country_of_issue = driver_country_of_issue
        customer_id.driver_date_of_issue = driver_date_of_issue
        customer_id.driver_date_of_expiry = driver_date_of_expiry
        customer_id.emirates_id_passport_number = emirates_id_passport_number
        customer_id.emirates_id_passport_date_of_issue = emirates_id_passport_date_of_issue
        customer_id.emirates_id_passport_date_of_expiry = emirates_id_passport_date_of_expiry
        customer_id.save()
        print("saved")
    except Exception as e:
        print(f"error as {e}")


    customer = {
    'column_names': [
        "customer_name",
        "customer_Dob",
        "customer_nationality",
        "Driver’s License No",
        "Country of Issue",
        "Date of Issue",
        "Date of Expiry",
        "Emirates ID/Passport No",
        "Emirates ID/Passport Date of Issue",
        "Emirates ID/Passport Date of Expiry",
    ],
    'values': [
        customer_name,
        customer_Dob,
        customer_nationality,
        driver_license_number,
        driver_country_of_issue,
        driver_date_of_issue,
        driver_date_of_expiry,
        emirates_id_passport_number,
        emirates_id_passport_date_of_issue,
        emirates_id_passport_date_of_expiry,
    ],
    }

    customer_info = [
        {"Name": customer_name},
        {"Date of Birth": customer_Dob},
        {"Nationality": customer_nationality},
        {"Driving License": driver_license_number},
        {"Country of Issue": driver_country_of_issue},
        {"Date of Issue": driver_date_of_issue},
        {"Date of Expiry": driver_date_of_expiry},
        {"Emirates ID": emirates_id_passport_number},
        {"ID Date of Issue": emirates_id_passport_date_of_issue},
        {"ID Date of Expiry": emirates_id_passport_date_of_expiry},
    ]
    


    Details = [customer_name, customer_Dob, customer_nationality, driver_license_number, driver_country_of_issue,
           driver_date_of_issue, driver_date_of_expiry, emirates_id_passport_number,
           emirates_id_passport_date_of_issue, emirates_id_passport_date_of_expiry]
    # zipped_data = zip(customer['values'], customer['column_names'])
    # print(customer_name)


    # for value, column_name in zipped_data:
    #     print(f"{column_name}: {value}")

    return render(request, 'ppmcontract.html', {'reports': report, 'forms': form,'customer_name':Details,'customer_info': customer_info})

#customer details excel importing
def customer_upload(request):
    if request.method == 'POST':
            form = CustomerExcelForm(request.POST,request.FILES)
            if form.is_valid():
                excel_files = form.cleaned_data['file']
                # Read Excel data using pandas
                df = pd.read_excel(excel_files)
                # Save data to the VehicleMaster model
                customer_data = []

                for index, row in df.iterrows():
                    
                    
                        instance = CustomerDetails(
                            Customer_ID=row['ID'],
                            name=row['Name'],
                            email=row['E-mail'],
                            phonenumber=row['Phone number'],
                            documentID=row['Document ID']            
                        )
                  
                        instance.save()
                        customer_data.append({
                        'Customer_ID': row['ID'],
                        'name': row['Name'],
                        'email': row['E-mail'],
                        'phonenumber': row['Phone number'],
                        'documentID': row['Document ID'],
                    })
            existing_customer_data = list(CustomerDetails.objects.values())
            print(existing_customer_data)
            return render(request, 'customer.html', {'form': form, 'customer_data': existing_customer_data})
                    # customer_data = df.to_dict(orient='records')                  
                    # request.session['bulk_upload_identifier'] = df
                    # request.session['bulk_upload_data'] = df.to_dict(orient='records')
                    # Convert lists of dictionaries to DataFrames
         
            # return render(request, 'customer.html',{'form': form, 'customer_data': customer_data})  # Pass the instance to the template

    else:
        customer_data = CustomerDetails.objects.order_by('-Customer_ID').values()

        paginator = Paginator(customer_data, 50)  # Show 50 items per page

        page_number = request.GET.get('page')
        try:
            customer_data = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            customer_data = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            customer_data = paginator.page(paginator.num_pages)

        form = CustomerExcelForm()
        return render(request, 'customer.html', {'form': form, 'customer_data': customer_data})

#merging two excel values
def merge_data(request):
    # Retrieve data from the CustomerDetails and VehicleDetails models
    customer_data = CustomerDetails.objects.values()
    vehicle_data = VehicleDetails.objects.values()

    # Convert database querysets to DataFrames
    customer_df = pd.DataFrame(customer_data)
    vehicle_df = pd.DataFrame(vehicle_data)

    # Merge data based on 'ID' and 'UserId'
    merged_data = pd.merge(customer_df, vehicle_df, left_on='ID', right_on='UserId', how='inner')

    # Convert merged data DataFrame to a list of dictionaries
    merged_data_list = merged_data.to_dict(orient='records') 
    return render(request, 'contractpdf.html', {'merged_data': merged_data_list})


#salik pageSalik list Yaldi hourly - total.xls
from datetime import datetime

def salik_Finance(request):
    if request.method == 'POST':
        form = SalikExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['file']
            df = pd.read_excel(excel_file)

            salik_data = []

            for index, row in df.iterrows():
                trip_date_str = str(row['Trip Date'])
                try:
                    # trip_date = datetime.strptime(trip_date_str, "%d %b %Y").date()
                    trip_date = datetime.strptime(trip_date_str, "%d %b %Y").date()

                except ValueError:
                    trip_date = None

                trip_time_str = str(row['Trip Time'])
                try:
                    trip_time = datetime.strptime(trip_time_str, "%I:%M:%S %p").time()
                except ValueError:
                    trip_time = None

                transactionID = row['Transaction ID']
                if transactionID != '-':
                    try:
                        transactionID = int(transactionID)
                    except ValueError:
                        transactionID = None
                    plate = str(row['Plate'])
                    matching_vehicle = VehicleDetails.objects.filter(Vehicle_No__icontains=plate).first()
                    print(matching_vehicle)
                    if matching_vehicle:
                        start_date = matching_vehicle.Start_date.date()
                        end_date = matching_vehicle.End_date.date()

                        if start_date <= trip_date <= end_date:
                            start_time = matching_vehicle.Start_date.time()
                            end_time = matching_vehicle.End_date.time()

                            if start_time <= trip_time <= end_time:
                                amount = row['Amount(AED)']
                                if amount != 0:
                                    user_id = matching_vehicle.UserId
                                    ride_id = matching_vehicle.Ride_ID

                                    # Check if a SalikDetails object already exists with the given transactionID
                                    existing_salik_instances = SalikDetails.objects.filter(TarnsactionID=transactionID)
                                    if existing_salik_instances.exists():
                                        # Update existing objects
                                        for salik_instance in existing_salik_instances:
                                            salik_instance.TripDate = trip_date
                                            salik_instance.TripTime = trip_time
                                            salik_instance.Plate = plate
                                            salik_instance.Ride_ID = ride_id
                                            salik_instance.UserId = user_id
                                            salik_instance.Amount = amount
                                            # salik_instance.Status = request.POST.get(f"status_{id}")  # Save status from dropdown
                                            salik_instance.save()
                                    else:
                                        # Create a new SalikDetails object
                                        instance = SalikDetails(
                                            TarnsactionID=transactionID,
                                            TripDate=trip_date,
                                            TripTime=trip_time,
                                            Plate=plate,
                                            Ride_ID=ride_id,
                                            UserId=user_id,
                                            Amount=amount
                                            # Status=request.POST.get(f"status_{id}")  # Save status from dropdown
                                        )
                                        instance.save()

                                    salik_data.append({
                                        'TarnsactionID': transactionID,
                                        'TripDate': trip_date,
                                        'TripTime': trip_time,
                                        'Plate': plate,
                                        'Ride_ID': ride_id,
                                        'UserId': user_id,
                                        'Amount': amount
                                        # 'Status': request.POST.get(f"status_{id}")  # Add status to vehicle_data
                                    })
            return render(request, 'salik.html', {'form': form, 'salik_data': salik_data})
    else:
        salik_data = SalikDetails.objects.order_by('-TarnsactionID').values()

        paginator = Paginator(salik_data, 50)  # Show 50 items per page

        page_number = request.GET.get('page')
        try:
            salik_data = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            salik_data = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            salik_data = paginator.page(paginator.num_pages)

        form = SalikExcelForm()
        return render(request, 'salik.html', {'form': form, 'salik_data': salik_data})




    


#fines excel upload views.py
def fines_excel(request):
    if request.method == 'POST':
        form = FinesExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['file']
            df = pd.read_excel(excel_file)

            fines_data = []
            # Iterate through each row in the dataframe
            for index, row in df.iterrows():
                ticket_date_str = str(row['Ticket Date'])
                if ticket_date_str.strip():  # Check if the date string is not empty
                    try:
                        ticket_date = datetime.strptime(ticket_date_str, "%d/%m/%Y").date()
                    except ValueError:
                        ticket_date = None
                else:
                    ticket_date = None

                ticket_time_str = str(row['Ticket Time'])
                try:
                    ticket_time = datetime.strptime(ticket_time_str, "%I:%M %p").time()
                except ValueError:
                    ticket_time = None
                  

                plate_no = str(row['Plate Number'])
                
                # Find matching vehicle details based on Plate Number
                matching_vehicle = VehicleDetails.objects.filter(Vehicle_No__icontains=plate_no).first()
                print(matching_vehicle)
                if matching_vehicle:
                    start_date = matching_vehicle.Start_date.date()
                    end_date = matching_vehicle.End_date.date()
                    
                    
                    # Check if Ticket Date is between Start Date and End Date of the ride
                    if start_date <= ticket_date <= end_date:
                        start_time = matching_vehicle.Start_date.time()
                        end_time = matching_vehicle.End_date.time()
                        
                        # Check if Ticket Time is between Start Time and End Time of the ride
                        if start_time <= ticket_time <= end_time:

                            ride_id = matching_vehicle.Ride_ID
                            # print(ride_id)
                            # Save data to FinesDetails model
                            instance = FinesDetails(
                                PlateNo=plate_no,
                                TicketNo=row['Ticket Number'],
                                TicketDate=ticket_date,
                                TicketTime=ticket_time,
                                FinesSource=row['Fines source'],  
                                TicketFee=row['Ticket Fee'],
                                Ride_ID=ride_id        
                            )
                            instance.save()

                            # Append data to fines_data list
                            fines_data.append({
                                'PlateNo': plate_no,
                                'TicketNo': row['Ticket Number'],
                                'TicketDate': ticket_date,
                                'TicketTime': ticket_time,
                                'FinesSource': row['Fines source'],
                                'TicketFee': row['Ticket Fee'],
                                'Ride_ID': ride_id
                            })
            
            # Render fines.html template with the form and fines_data
            return render(request, 'fines.html', {'form': form, 'fines_data': fines_data})
    else:
        # If the request method is not POST, render the fines.html template with the form and existing fines data
        fines_data = list(FinesDetails.objects.order_by('-PlateNo').values())
        paginator = Paginator(fines_data, 50)  # Show 50 items per page

        page_number = request.GET.get('page')
        try:
            fines_data = paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            fines_data = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            fines_data = paginator.page(paginator.num_pages)
                  # Debugging line
        form = FinesExcelForm()
        return render(request, 'fines.html', {'form': form, 'fines_data': fines_data})



#user adding page
from .models import UserSaving  # Import your User model

def users_adding(request):
    print(request.session.get('useraccess'))
    if request.method == 'POST':
        form = UserSavingForm(request.POST)
        if form.is_valid():
            new_user = form.save()  # Save the user data to the database
            return redirect('users_adding')  # Redirect to the users page after successful form submission
        else:
            errors = form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)
    else:
        # Fetch existing user data
        existing_users = UserSaving.objects.all()  # You may need to adjust this query based on your model structure
        return render(request, 'users.html', {'data': existing_users})
    
#user page delete button
def delete_user(request, id):
    print("delete okk")
    if request.method == 'DELETE':
        try:
            user = UserSaving.objects.get(id=id)
            print(user)
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'})
        except UserSaving.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


#edit user details
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import UserSaving

def edit_user(request, id):
    if request.method == 'POST':
        user = get_object_or_404(UserSaving, id=id)
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.password = request.POST.get('password')
        user.save()
        return JsonResponse({'message': 'User updated successfully'})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
#status  in vehicledetails
from django.http import JsonResponse

def update_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('userId')
        status = data.get('status')
        
        try:
            # Retrieve the VehicleDetails object with the given user_id
            vehicle = VehicleDetails.objects.get(UserId=user_id)
            # Update the status
            vehicle.Status = status
            vehicle.save()
            
            # Return a success response
            return JsonResponse({'success': True, 'status': status})
        except VehicleDetails.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'}, status=404)
    else:
        # If the request method is not POST or it's not an AJAX request, return an error response
        return JsonResponse({'success': False, 'error': 'Invalid request'})


#salik statusviews.py
def salik_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        transaction_id = data.get('transactionId')
        status = data.get('status')
        try:
            # Retrieve the VehicleDetails object with the given user_id
            vehicle = SalikDetails.objects.get(TarnsactionID=transaction_id)
            # Update the status
            vehicle.Status = status
            vehicle.save()
            
            # Return a success response
            return JsonResponse({'success': True, 'status': status})
        except VehicleDetails.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'}, status=404)
    else:
        # If the request method is not POST or it's not an AJAX request, return an error response
        return JsonResponse({'success': False, 'error': 'Invalid request'})


#salik statusviews.py
def fines_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        plate_no = data.get('plateno')
        status = data.get('status')
        try:
            # Retrieve the VehicleDetails object with the given user_id
            vehicle = SalikDetails.objects.get(PlateNo=plate_no)
            # Update the status
            vehicle.Status = status
            vehicle.save()
            
            # Return a success response
            return JsonResponse({'success': True, 'status': status})
        except VehicleDetails.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vehicle not found'}, status=404)
    else:
        # If the request method is not POST or it's not an AJAX request, return an error response
        return JsonResponse({'success': False, 'error': 'Invalid request'})


#excel file export button
import json
import csv
import requests
from django.http import HttpResponse
from django.utils import timezone
from .models import VehicleDetails

def generate_csv(request):
    # Retrieve data from the database
    userid = request.GET.get('UserId')
    vehicle_details = VehicleDetails.objects.all()
    

    # Prepare the response as CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehicle_datafile.csv"'

    # Define the CSV column names
    csv_columns = [
        'Trip ID', 'VIN', 'VRN', 'Transport Operator Name', 'Driver Permit Number',
        'Driver Permit Type', 'Driver License Number', 'Start Time (UTC)', 'Start Position Latitude',
        'Start Position Longitude','End Time (UTC)','End Position Latitude','End Position Longitude',
        'Start Position Name','Planned Destination Name','Book Channel','Book Time (UTC)',
        'Trip Time (Seconds)','Status','Payment Type','Reason','Distance (Meters)',
        'Fare Amount','Start Fare','Fare Distance Charge','Fare Time Charge','Tollways',
        'Fare Extra','Fare Tax','Fare Tips','Fare Rate','Fare Unit','Booking Fee',
        'Waiting Fee','Promotion-Code','Promotion-Type','Promotion Amount','City-Change-Charge',
        'City-Change-Code','Fix-Charge'
    ]

    # Write data to CSV file
    writer = csv.DictWriter(response, fieldnames=csv_columns)
    writer.writeheader()

    
    for vehicle in vehicle_details:
        customers = CustomerDetails.objects.filter(Customer_ID=vehicle.UserId)
        # print("Customer Details for Vehicle ID:", vehicle.UserId)
        # print("Start:",vehicle.Start_date)
        # print("End:",vehicle.End_date)
        difference = vehicle.End_date-vehicle.Start_date
        # print("Difference:",difference)
        if difference <= timedelta(hours=24):
            for customer in customers:
                start_time_utc = vehicle.Start_date.astimezone(timezone.utc)
                end_time_utc = vehicle.End_date.astimezone(timezone.utc)
            # Convert ride duration to seconds
                ride_duration_seconds = vehicle.Ride_duration.total_seconds()
                writer.writerow({
                        'Trip ID': vehicle.Ride_ID,
                        'VIN': '',  
                        'VRN': vehicle.Vehicle_No,
                        'Transport Operator Name': 'YALDI HOURLY CAR RENTAL L.L.C',
                        'Driver Permit Number': '',
                        'Driver Permit Type': '',
                        'Driver License Number': customer.driver_license_number,
                        'Start Time (UTC)': start_time_utc,
                        'Start Position Latitude' : vehicle.Vehiclestartlatitude,
                        'Start Position Longitude': vehicle.Vehiclestartlongitude,
                        'End Time (UTC)': end_time_utc,
                        'End Position Latitude': vehicle.Vehicleendlatitude,
                        'End Position Longitude': vehicle.Vehicleendlongitude,
                        'Start Position Name': '',
                        'Planned Destination Name': '',
                        'Book Channel': 'others',
                        'Book Time (UTC)': start_time_utc.date().strftime("%Y-%m-%d"),  # Date portion of start time in UTC
                        'Trip Time (Seconds)': ride_duration_seconds,  # Ride duration in seconds
                        'Status': 'FINISHED',
                        'Payment Type': '',
                        'Reason': '',
                        'Distance (Meters)': vehicle.Ride_distance * 1000,  # Distance in meters
                        'Fare Amount': vehicle.Total_cost,
                        'Start Fare': '',
                        'Fare Distance Charge': '',
                        'Fare Time Charge': '',
                        'Tollways': '',
                        'Fare Extra': '',
                        'Fare Tax': '',
                        'Fare Tips': '',
                        'Fare Rate': '',
                        'Fare Unit': '',
                        'Booking Fee': '',
                        'Waiting Fee': '',
                        'Promotion-Code': '',
                        'Promotion-Type': '',
                        'Promotion Amount': '',
                        'City-Change-Charge': '',
                        'City-Change-Code': '',
                        'Fix-Charge': ''
                    })
        else:
            print(f"more than 24 hourse {vehicle.UserId}")
            continue
        
        # try:
        #     customer_id = CustomerDetails.objects.get(ID=userid)
        #     customer_sumsub = customer_id.documentID
        #     print(customer_sumsub)
        #     SUMSUB_TEST_BASE_URL = "https://api.sumsub.com"
        #     id=customer_sumsub
        #     url = f"{SUMSUB_TEST_BASE_URL}/resources/applicants/{id}/one"
        #     resp = requests.get(url)
        
        #     if resp.status_code == 200:  # Check if request is successful
        #         response_data = resp.json()  # Parse response JSON
        #         # Initialize variables
        #         driver_license_number = ''
        #         # Iterate through idDocs
        #         for id_doc in response_data.get('info', {}).get('idDocs', []):
        #             doc_type = id_doc.get('idDocType', '')
        #             if doc_type == 'DRIVERS':
        #                 # Driver’s License
        #                 driver_license_number = id_doc.get('number', '')
        #                 break  # Exit the loop once driver's license number is found

        #         # Convert start and end time to UTC format using timezone
        #         start_time_utc = vehicle.Start_date.astimezone(timezone.utc)
        #         end_time_utc = vehicle.End_date.astimezone(timezone.utc)
            
        #         # Convert ride duration to seconds
        #         ride_duration_seconds = vehicle.Ride_duration.total_seconds()

        #         writer.writerow({
        #             'Trip ID': vehicle.Ride_ID,
        #             'VIN': '',  
        #             'VRN': vehicle.Vehicle_No,
        #             'Transport Operator Name': 'YALDI HOURLY CAR RENTAL L.L.C',
        #             'Driver Permit Number': '',
        #             'Driver Permit Type': '',
        #             'Driver License Number': driver_license_number,
        #             'Start Time (UTC)': start_time_utc,
        #             'Start Position Latitude' : vehicle.Vehiclestartlatitude,
        #             'Start Position Longitude': vehicle.Vehiclestartlongitude,
        #             'End Time (UTC)': end_time_utc,
        #             'End Position Latitude': vehicle.Vehicleendlatitude,
        #             'End Position Longitude': vehicle.Vehicleendlongitude,
        #             'Start Position Name': '',
        #             'Planned Destination Name': '',
        #             'Book Channel': 'others',
        #             'Book Time (UTC)': start_time_utc.date().strftime("%Y-%m-%d"),  # Date portion of start time in UTC
        #             'Trip Time (Seconds)': ride_duration_seconds,  # Ride duration in seconds
        #             'Status': 'FINISHED',
        #             'Payment Type': '',
        #             'Reason': '',
        #             'Distance (Meters)': vehicle.Ride_distance * 1000,  # Distance in meters
        #             'Fare Amount': vehicle.Total_cost,
        #             'Start Fare': '',
        #             'Fare Distance Charge': '',
        #             'Fare Time Charge': '',
        #             'Tollways': '',
        #             'Fare Extra': '',
        #             'Fare Tax': '',
        #             'Fare Tips': '',
        #             'Fare Rate': '',
        #             'Fare Unit': '',
        #             'Booking Fee': '',
        #             'Waiting Fee': '',
        #             'Promotion-Code': '',
        #             'Promotion-Type': '',
        #             'Promotion Amount': '',
        #             'City-Change-Charge': '',
        #             'City-Change-Code': '',
        #             'Fix-Charge': ''
        #         })
        #     else:
        #         # Handle API request failure gracefully
        #         print(f"Failed to fetch SUMSUB data for UserId: {vehicle.UserId}")
        # except CustomerDetails.DoesNotExist:
        #     print(f"CustomerDetails not found for UserId: {vehicle.UserId}")
        # except Exception as e:
        #     print(f"Error processing vehicle: {vehicle.id}, Error: {str(e)}")

    return response






















# -----------------------------------------------------------------------------------------------------------

# from django.shortcuts import render, redirect
# from .models import VehicleDetails  # Import your model

def form_submit(request):
    if request.method == 'POST':
        # Assuming your form fields match the model fields
        vehicle_no = request.POST.get('Vehicle_No')
        ride_distance_str = request.POST.get('Ride_distance')
        start_date_str = request.POST.get('Start_date')
        end_date_str = request.POST.get('End_date')
        ride_duration_str = request.POST.get('Ride_duration')
        total_cost_str = request.POST.get('Total_cost')


        # Check and parse date strings
        
        start_date = parsedate(start_date_str) if start_date_str else None
        end_date = parsedate(end_date_str) if end_date_str else None

        if not start_date or not end_date:
            # Handle invalid date format or empty date strings
            # You might want to redirect the user to the form with an error message
            return render(request, 'ppmcontract.html', {'error': 'Invalid date format'})

        # Check if ride_distance_str is not empty
        if ride_distance_str:
            # Convert ride_distance_str to Decimal
            ride_distance = Decimal(ride_distance_str)
        else:
            # Handle the case where ride_distance_str is empty (you might want to set a default value)
            ride_distance = Decimal(0)

        # Check if total_cost_str is not empty
        if total_cost_str:
            # Convert total_cost_str to Decimal
            total_cost = Decimal(total_cost_str)
        else:
            # Handle the case where total_cost_str is empty (you might want to set a default value)
            total_cost = Decimal(0)

          # Check if ride_duration_str is not empty
        if ride_duration_str:
            # Convert ride duration string to timedelta
            hours, minutes, seconds = map(int, ride_duration_str.split(':'))
            ride_duration_timedelta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        else:
            # Handle the case where ride_duration_str is empty (you might want to set a default value)
            ride_duration_timedelta = timedelta()
        # Create an instance of your model and save the data
        instance = VehicleDetails(
            Vehicle_No=vehicle_no,
            Ride_distance=ride_distance,
            Start_date=start_date,
            End_date=end_date,
            Ride_duration=ride_duration_timedelta,
            Total_cost=Decimal(total_cost)
        )
        
        instance.save()

        # Redirect to a success page or render a template with the saved data
        return redirect('submit-form/')  # Change 'success_page' to the actual URL name

    return render(request, 'ppmcontract.html')  # Render the form template for GET requests









    







               