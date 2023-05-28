from django.shortcuts import render,redirect,HttpResponse
from company.models import Company,Branches
from django.contrib import auth,messages
from django.contrib.auth import logout,authenticate, login
import mysql.connector
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.mail import send_mail
from smtplib import SMTPAuthenticationError
import face_recognition
import pickle
import cv2
import numpy as np
import bcrypt
import datetime
from tensorflow import keras
from tensorflow.keras.utils import img_to_array,array_to_img
# Create your views here.

# company registration function
def signup(request):
    if request.method=='POST':
        company_name=request.POST['company_name']
        company_founder=request.POST['company_founder']
        established=request.POST['established']
        company_contact=request.POST['company_contact']
        company_email=request.POST['company_email']
        company_password=request.POST["password"]
        company_password = make_password(company_password)
        company_url=request.POST['company_url']
        mainbranch_name=request.POST['mainbranch_name']
        mainbranch_latitude=float(request.POST['branch_latitude'])
        mainbranch_longitude=float(request.POST['branch_longitude'])
        mainbranch_area=request.POST['branch_area']
        if Company.objects.filter(company_name=company_name).exists()==False:
            if Company.objects.filter(company_mail=company_email).exists()==False:
                if Company.objects.filter(company_url=company_url).exists()==False:
                    comp_count=Company.objects.all().count()
                    comp_count+=1
                    company_id="C"+str(comp_count)
                    company=Company(company_id=company_id,company_name=company_name,founder=company_founder,
                    established_date=established,company_contact=company_contact,
                    company_mail=company_email,company_password=company_password,company_url=company_url)
                    company.save()
                    branch_count=Branches.objects.filter(company_id=company_id).count()
                    branch_count+=1
                    Branch_id="B"+str(branch_count)
                    main_branch=Branches(Branch_id=Branch_id,Branch_name=mainbranch_name,Branch_lat=mainbranch_latitude,
                    Branch_long=mainbranch_longitude,Branch_range=mainbranch_area,is_main=True,company_id=company_id)
                    main_branch.save()
                    cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                    cursor = cnx.cursor()
                    holiday_table="create table "+company_name+"_"+Branch_id+"""_holidays (
                    holiday_date DATE primary key,
                    holiday_name VARCHAR(255) NOT NULL

                    )"""
                    
                    cursor.execute(holiday_table)
                    cnx.commit()
                    create_table="create table "+company_name+"""(
                            employee_id nvarchar(30) primary key,
                            branch_id varchar(50) NOT NULL,   
                            first_name nvarchar(50) not null,
                            last_name nvarchar(50) not null,
                            email nvarchar(100) unique  not null,
                            emp_password nvarchar(255) not null,
                            face_encodings blob,
                            designation nvarchar(30) not null,
                            reports_to nvarchar(30),
                            is_root integer check (is_root=1 or is_root=0),
                            is_admin integer check (is_admin=1 or is_admin=0),
                            mobile nvarchar(10) not null,
                            gender nvarchar(10) not null,
                            address  nvarchar(250) not null,
                            dob date,
                            blood_group nvarchar(10) not null,
                            father_name nvarchar(50) not null,
                            doj date,
                            nationality nvarchar(50) not null,
                            marital_status nvarchar(50) not null,
                            religion nvarchar(50) not null,
                            pan nvarchar(20) not null,
                            education nvarchar(50) not null,
                            university nvarchar(50) not null,
                            disabled integer check (disabled=1 or disabled=0),
                            employee_image longblob,
                            leave_count integer,
                            foreign key(branch_id) references companies.company_branches(branch_id),
                            foreign key(reports_to) references """+company_name+"(employee_id))"
                            
                    cursor.execute(create_table)
                    if cursor.rowcount == 0:
                        cnx.commit()

                        create_attend="create table "+company_name+"""_attendance(
                            employee_id nvarchar(30),
                            branch_id varchar(50) NOT NULL,
                            date date,
                            logged_in TIMESTAMP,
                            logged_out TIMESTAMP,
                            primary key (employee_id,date),
                            foreign key(branch_id) references companies.company_branches(branch_id))"""
                        cursor.execute(create_attend)
                        if cursor.rowcount == 0:
                            cnx.commit()
                            create_leave="create table "+company_name+"""_leaves(
                            employee_id nvarchar(30),
                            branch_id varchar(50) NOT NULL,
                            from_date date,
                            to_date date,
                            leave_type nvarchar(30) check  (leave_type='paid leave' or leave_type='bereavement leave' or leave_type='Maternity and Paternity Leave' or leave_type='Leave with out pay'),
                            status nvarchar(30) check  (status='applied' or status='approved' or status='rejected'),
                            primary key (employee_id,from_date,to_date),
                            foreign key(branch_id) references companies.company_branches(branch_id))"""
                            cursor.execute(create_leave)
                            if cursor.rowcount == 0:
                                cnx.commit()
                                cursor.close()
                                cnx.close()
                                messages.success(request,'company registered successfully! please login as '+company_id+' to continue')
                                return redirect('/company/company_login')
                            else:
                                cursor.execute("drop table "+company_name)
                                cursor.execute("drop table "+company_name+"_attendance")
                                cursor.close()
                                cnx.close()
                                messages.warning(request,'Technical error, please try again')
                                main_branch.delete()
                                company.delete()
                                
                                return redirect('/company/signup')
                        else:
                            cursor.close()
                            cnx.close()
                            messages.warning(request,'Technical error, please try again')
                            main_branch.delete()
                            company.delete()
                            cnx.execute("drop table "+company_name)
                            return redirect('/company/signup')

                        
                    else:
                        cursor.close()
                        cnx.close()
                        messages.warning(request,'company registration failed')
                        main_branch.delete()
                        company.delete()
                        return redirect('/company/signup')

                else:
                    messages.warning(request,'URL is already taken')
                    return redirect('/company/signup')
            else:
                messages.warning(request,'mail is already taken')
                return redirect('/company/signup')
        else:
            messages.warning(request,'Company Name is already taken')
            return redirect('/company/signup')

    else:
        return render(request,'signup.html')

def company_login(request):
    if request.method == 'POST':
        password = request.POST['password']
        company_id=request.POST['company_id']
        company = Company.objects.filter(company_id=company_id).first()
        if company is not None:
            
            if check_password(password, company.company_password):
                request.session['company_id'] = company.company_id
                request.session['company_name'] = company.company_name
                return redirect('home')
            else:
                messages.warning(request,'Incorrect Password')
                return render(request, 'company_login.html')
        else:
            messages.warning(request,'Invalid Company ID')
            return render(request, 'company_login.html')
    else:
       
        return render(request, 'company_login.html')



def login(request):
    if request.method == 'POST':
        employee_id = request.POST['employee_id']
        password = request.POST['password']
        company_id=request.POST['company_id']
        branch_id=request.POST['branch_id']
        company = Company.objects.filter(company_id=company_id).first()
        if company is not None:
            company_name=company.company_name
            cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
            cursor = cnx.cursor()
            query="select * from "+company_name+" where employee_id="+"'"+employee_id+"'"
            cursor.execute(query)
            user=cursor.fetchone()
            cursor.close()
            cnx.close()
            if len(user)>0:
                if check_password(password,user[5]):
                    request.session['employee_id'] = user[0]
                    request.session['employee_name'] = user[2]
                    request.session['company_name'] = company_name
                    if user[9]==1:
                        request.session['root'] = user[9]
                    elif user[10]==1:
                        request.session['admin'] = user[10]
                    return redirect('home')
                else:
                    messages.warning(request,'Invalid Employee ID')
                    return render(request, 'login.html')
            else:
                messages.warning(request,'Incorrect Password')
                return render(request, 'login.html')
        else:
            messages.warning(request,'Invalid Company ID')
            return render(request, 'login.html')
    else:
        
        return render(request, 'login.html')

def logout(request):
    
    if 'employee_id' in request.session:
        request.session.clear()
    elif 'company_id' in request.session:
        request.session.clear()
    return redirect('/')

def register_employe(request):
    if request.method=='POST':
        is_authorized=False
        if 'employee_id' in request.session or 'company_id' in request.session:
            employee_id=request.POST['employee_id']
            branch_id=request.POST['branch_id']
            designation=request.POST['designation']
            employee_image=request.FILES.get('employee_image')
            reports_to=request.POST['reports_to']
            employee_email=request.POST['employee_email']
            employee_password=request.POST['employee_password']
            employee_password=make_password(employee_password)
            employee_fname=request.POST['employee_fname']
            employee_lname=request.POST['employee_lname']
            employee_mobile=request.POST['employee_mobile']
            gender=request.POST['gender']
            street=request.POST['street']
            city=request.POST['city']
            state=request.POST['state']
            pincode=request.POST['pincode']
            dob=request.POST['dob']
            
            employee_father=request.POST['employee_father']
            blood_group=request.POST['blood_group']
            doj=request.POST['doj']
            
            nationality=request.POST['nationality']
            religion=request.POST['religion']
            marital_status=request.POST['marital_status']
            pan=request.POST['pan']
            education=request.POST['education']
            university=request.POST['university']
            disabled=request.POST['disabled']
            if disabled == 'yes':
                disabled=1
            else:
                disabled=0
            is_root=0
            is_admin=0
            address=street+","+city+","+state+"-"+pincode
            if employee_image:
                
                employee_image=face_recognition.load_image_file(employee_image)

                image=face_recognition.face_encodings(employee_image)[0]
                image=pickle.dumps(image)
                original_image=img_to_array(employee_image)
                original_image=pickle.dumps(original_image)
            else:
                messages.warning(request,'Technical error while loading image, please try again')
                return redirect('/company/register_employe')
            if 'company_id' in request.session:
                is_authorized=True
                is_root=request.POST['root']
                is_admin=request.POST['admin']
                if is_root=='yes':
                    is_root=1
                else:
                    is_root=0
                if is_admin=='yes':
                    is_admin=1
                else:
                    is_admin=0
            elif 'employee_id' in request.session:
                cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                cursor = cnx.cursor()
                company_name=request.session['company_name']
                query="select * from "+company_name+" where employee_id="+"'"+request.session['employee_id']+"'"
                cursor.execute(query)
                user=cursor.fetchone()
                cursor.close()
                cnx.close()
                if len(user)>0:
                    if(user[9]==1):
                        is_authorized=True
                        is_root=request.POST['root']
                        is_admin=request.POST['admin']
                        if is_root=='yes':
                            is_root=1
                        else:
                            is_root=0
                        if is_admin=='yes':
                            is_admin=1
                        else:
                            is_admin=0
                    elif (user[10]==1):
                        is_authorized=True
                        is_admin=request.POST['admin']
                        if is_admin=='yes':
                            is_admin=1
                        else:
                            is_admin=0
                    else:
                        messages.warning(request,'you are not authorized to add an employee')
                        return redirect('/')
                else:
                    messages.warning(request,'you are not authorized to add employee')
                    return redirect('/')
            else:
                    messages.warning(request,'you are not authorized to add employee')
                    return redirect('/')
            if is_authorized:
                cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                cursor = cnx.cursor()
                company_name=request.session['company_name']
                query="insert into "+company_name+"(employee_id,branch_id,first_name,last_name,email,emp_password,face_encodings,designation,reports_to,is_root,is_admin,mobile,gender,address,dob,blood_group,father_name,doj,nationality,marital_status,religion,pan,education,university,disabled,employee_image,leave_count) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                result=cursor.execute(query,(employee_id,branch_id,employee_fname,employee_lname,employee_email,employee_password,image,designation,reports_to,is_root,is_admin,employee_mobile,gender,address,dob,blood_group,employee_father,doj,nationality,marital_status,religion,pan,education,university,disabled,original_image,3))
                if result is None:
                    cnx.commit()
                    cursor.close()   
                    cnx.close()
                    messages.success(request,'Employee added successfully')
                    return redirect('home') 
                else:
                    cursor.close()
                    cnx.close()
                    messages.warning(request,'Technical error, please try again')
                    return redirect('/company/register_employe')
            else:
                messages.warning(request,'you are not authorized to add employee')
                return redirect('/')

        else:
            messages.warning(request,'you are not authorized to add employee')
            return redirect('/')

    else:
        if 'employee_id' in request.session:
            cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
            cursor = cnx.cursor()
            company_name=request.session['company_name']
            query="select * from "+company_name+" where employee_id="+"'"+request.session['employee_id']+"'"
            cursor.execute(query)
            user=cursor.fetchone()
            cursor.close()
            cnx.close()
            if len(user)>0:
                if(user[9]==1 or user[10]==1):
                    return render(request,'register.html')
                else:
                    messages.warning(request,'you are not authorized to add an employee')
                    return redirect('/')
            else:
                messages.warning(request,'unable to fetch details, please try again')
                return redirect('/')
        elif 'company_id' in request.session:
            return render(request,'register.html')
        else:
            messages.warning(request,'please login to register employess')
            return redirect('/')



def send_otp(request):
    if request.method == 'POST':
        email = request.POST['email']
        otp = request.POST['otp']
        try:
            send_mail(
                'OTP',
                f'Your OTP is {otp}',
                'mahantidurgamohan999@gmail.com',
                [email],
                fail_silently=False,
            )
        except SMTPAuthenticationError as e:
            print(e)
            return JsonResponse({'message': 'SMTP authentication failed'}, status=500)

        except Exception as e:
            return JsonResponse({'message': 'An error occurred while sending the email'}, status=500)

        # store the OTP in the database and associate it with the email address
        return JsonResponse({'message': 'OTP sent'})

def swipe_in(request):
    # checking if employee is logged in
    if 'employee_id' in request.session:
        company_name=request.session['company_name']
        cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
        cursor = cnx.cursor()
        get_leave="select * from "+company_name+"_leaves where employee_id='"+request.session['employee_id']+"'"
        query1="select * from "+company_name+" where employee_id="+"'"+request.session['employee_id']+"'"
        query2="select max(date) from "+company_name+"_attendance where employee_id='"+request.session['employee_id']+"'"
        cursor.execute(query1)
        user=cursor.fetchone()
        cursor.execute(query2)
        prev_date=str(cursor.fetchone()[0])
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        if now.weekday()==5 or now.weekday()==6:
            cursor.close()
            cnx.close()
            messages.warning(request,'today is a non working day')
            return redirect('home')
        
        if prev_date!= 'None':
            query3="SELECT logged_out FROM "+company_name+"_attendance where date="+"'"+prev_date+"'"+" and employee_id='"+request.session['employee_id']+"'"
           
        
            cursor.execute(query3)
            prev_loggedout=cursor.fetchone()
        else:
            prev_loggedout=1

        
        #checking if user exists in database of the company
        if len(user)>0:
            leave_query="SELECT * FROM {} WHERE  from_date<=%s and %s<=to_date and employee_id='"+request.session['employee_id']+"'"
            table_name=company_name+'_leaves'
            cursor.execute(leave_query.format(table_name), (current_date, current_date))
            leave_result=cursor.fetchall()
            
            if len(leave_result)>0:
                cursor.close()
                cnx.close()
                messages.warning(request,'you applied leave for today, you cannot swipe in')
                return redirect('home')
            holidays_query="SELECT holiday_date FROM "+company_name+"_"+user[1]+"_holidays"
            cursor.execute(holidays_query)
            holidays=cursor.fetchall()
            for holiday in holidays:
                if str(holiday[0])==current_date:
                    cursor.close()
                    cnx.close()
                    messages.warning(request,'you cannot swipe in on a holiday')
                    return redirect('home')
            
            if prev_loggedout is not None:
                image_of_emp=user[6]
                branch_id=user[1]
                #deserializing the image array stored in table
                image_of_emp=pickle.loads(image_of_emp)
                #taking the pic of the employee using web cam for verification
                cam = cv2.VideoCapture(0)
                result, image = cam.read()
                cam.release()
                #resizing the image 
                image = cv2.resize(image, (0, 0), None, 0.25, 0.25)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                #checking if image is captured by web cam
                if result:
                    #taking the face locations from the captured image
                    face_locs=face_recognition.face_locations(image)
                    #checking if atleast one face is there
                    if len(face_locs)>0:
                        #encoding those faces
                        face_encods=face_recognition.face_encodings(image,face_locs)
                        #checking atleast one face is encoded
                        if len(face_encods)>0:
                            matches = face_recognition.compare_faces(image_of_emp, face_encods)
                            faceDis = face_recognition.face_distance(image_of_emp, face_encods)
                            matchIndex = np.argmin(faceDis)
                            result=matches[matchIndex]
                            
                            if result == True:
                                # Get the current date and time
                                
                                current_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                                if current_date==prev_date:
                                    messages.warning(request,'your attendance for the day has already marked , please swipe in tomorrow')
                                    return redirect('home')
                                else:
                                    cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                                    cursor = cnx.cursor()
                                    # Insert the data into the database
                                    sql = "INSERT INTO "+company_name+"_attendance (employee_id,branch_id,date,logged_in) VALUES (%s,%s,%s, %s)"
                                    val = (request.session['employee_id'],branch_id,current_date, current_timestamp)
                                    
                                    cursor.execute(sql, val)
                                    
                                    cnx.commit()
                                    cursor.close()
                                    cnx.close()
                                    messages.success(request,'you are verified and attendance captured')
                                    return redirect('home')
                                
                            else:
                                messages.warning(request,'you are not verified')
                                return redirect('home')
                        else:

                            messages.warning(request,'No face detected try again')
                            return redirect('home')
                        

                    
                    else:
                        messages.warning(request,'No face detected try again')
                        return redirect('home')
                else:
                    return redirect('/company/swipe_in')
            else:
                messages.warning(request,'please swipe out from previous swipe in first!')
                return redirect('home')
        else:
            return redirect('home')
    else:
        messages.warning(request,'please login as employee to mark attendance')
        return redirect('/company/login')

def swipe_out(request):
    # checking if employee is logged in
    if 'employee_id' in request.session:

        company_name=request.session['company_name']
        cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
        cursor = cnx.cursor()
        query1="select * from "+company_name+" where employee_id="+"'"+request.session['employee_id']+"'"
        
        query2="select max(date) from "+company_name+"_attendance where employee_id='"+request.session['employee_id']+"'"
        print(query2)
        cursor.execute(query1)
        user=cursor.fetchone()
        cursor.execute(query2)
        prev_date=str(cursor.fetchone()[0])
        query3="SELECT logged_out FROM "+company_name+"_attendance where date= '"+prev_date+"' and employee_id='"+request.session['employee_id']+"'"
        print(query3)
        cursor.execute(query3)
        prev_loggedout=cursor.fetchone()[0]
        print(prev_loggedout)
        cursor.close()
        cnx.close()
        #checking if user exists in database of the company
        if len(user)>0:
            if prev_loggedout is None:
                image_of_emp=user[6]
                branch_id=user[1]
                #deserializing the image array stored in table
                image_of_emp=pickle.loads(image_of_emp)
                #taking the pic of the employee using web cam for verification
                cam = cv2.VideoCapture(0)
                result, image = cam.read()
                cam.release()
                #resizing the image 
                image = cv2.resize(image, (0, 0), None, 0.25, 0.25)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                #checking if image is captured by web cam
                if result:
                    #taking the face locations from the captured image
                    face_locs=face_recognition.face_locations(image)
                    #checking if atleast one face is there
                    if len(face_locs)>0:
                        #encoding those faces
                        face_encods=face_recognition.face_encodings(image,face_locs)
                        #checking atleast one face is encoded
                        if len(face_encods)>0:
                            matches = face_recognition.compare_faces(image_of_emp, face_encods)
                            faceDis = face_recognition.face_distance(image_of_emp, face_encods)
                            matchIndex = np.argmin(faceDis)
                            result=matches[matchIndex]
                            
                            if result == True:
                                # Get the current date and time
                                now = datetime.datetime.now()
                                current_date = now.strftime("%Y-%m-%d")
                                current_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                                cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                                cursor = cnx.cursor()
                                # Insert the data into the database
                                sql = "update "+company_name+"_attendance set logged_out= '"+current_timestamp+"'"+" where date="+"'"+prev_date+"'"+" and employee_id='"+request.session['employee_id']+"'"
                               
                                cursor.execute(sql)
                                
                                cnx.commit()
                                cursor.close()
                                cnx.close()
                                messages.success(request,'you are verified and attendance captured')
                                return redirect('home')
                                
                            else:
                                messages.warning(request,'you are not verified')
                                return redirect('home')
                        else:

                            messages.warning(request,'No face detected try again')
                            return redirect('home')
                        

                    
                    else:
                        messages.warning(request,'No face detected try again')
                        return redirect('home')
                else:
                    return redirect('/company/swipe_in')
            else:
                messages.warning(request,'please swipe in first')
                return redirect('home')
        else:
            return redirect('home')
    else:
        messages.warning(request,'please login as employee to mark attendance')
        return redirect('/company/login')

def add_branch(request):
    if request.method=='POST':
        if 'company_id' in request.session:
            branch_name=request.POST["branch_name"]
            branch_latitude=request.POST["branch_latitude"]
            branch_longitude=request.POST["branch_longitude"]
            branch_area=request.POST["branch_area"]
            company_id=request.session['company_id']
            company_name=request.session['company_name']
            if Branches.objects.filter(Branch_name=branch_name,company_id=company_id).exists()==False:
                branch_count=Branches.objects.filter(company_id=company_id).count()
                branch_count+=1
                Branch_id="B"+str(branch_count)
                branch=Branches(Branch_id=Branch_id,Branch_name=branch_name,Branch_lat=branch_latitude,
                Branch_long=branch_longitude,Branch_range=branch_area,is_main=False,company_id=company_id)
                branch.save()
                cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                cursor = cnx.cursor()
                holiday_table="create table "+company_name+"_"+Branch_id+"""_holidays (
                holiday_date DATE primary key,
                holiday_name VARCHAR(255) NOT NULL

                )"""
                cursor.execute(holiday_table)
                cnx.commit()
                cursor.close()
                cnx.close()
                messages.success(request,'branch added successfully')
                return redirect('/')
            else:
                messages.warning(request,'Branch Name already taken')
                return redirect('/company/add_branch')
        else:
            messages.warning(request,'you are not allowed to add branch')
            return redirect('/')
              
    else:
        if 'company_id' in request.session:
            return render(request,'add_branch.html')
        else:
            messages.warning(request,'you are not allowed to the page')
            return redirect('/')
    

def leave(request):
    if 'employee_id' in request.session:
        if request.method=='POST':
            employee_id=request.session['employee_id']
            branch_id=request.POST["branch_id"]
            from_date=request.POST["from_date"]
            to_date=request.POST["to_date"]
            leave_type=request.POST["leave_type"]
            company_name=request.session['company_name']
            try:
                cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                cursor = cnx.cursor()
                check_employee="select * from "+company_name+" where employee_id="+"'"+employee_id+"'"
                cursor.execute(check_employee)
                employee=cursor.fetchone()
                if len(employee)>0:
                    query="""SELECT *
                            FROM """+company_name+"""_leaves 
                            WHERE ((from_date <= '"""+to_date+"""' AND to_date >= '"""+from_date+"""')
                            OR (from_date <= '"""+from_date+"""' AND to_date >= '"""+to_date+"""')) and status <> 'rejected'
                            and employee_id='"""+employee_id+"'"
                    print(query)
                    cursor.execute(query)
                    result=cursor.fetchall()
                    if len(result)==0:
                        if leave_type=='paid leave':
                            leave_balance=employee[26]
                             # Convert the input dates to datetime objects
                            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d')
                            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d')
                            
                            # Calculate the difference in days
                            date_diff = (to_date_obj - from_date_obj).days+1
                            if date_diff>leave_balance:
                                messages.warning(request,'you do not have enough paid leaves , please select the appropriate type ')
                                return redirect('/')
                            
                        insert="insert into "+company_name+"""_leaves (employee_id,branch_id,from_date,to_date,leave_type,status)
                        values (%s,%s,%s,%s,%s,%s)"""
                        cursor.execute(insert,(employee_id,branch_id,from_date,to_date,leave_type,'applied'))
                        cnx.commit()
                        leave_count=leave_balance-date_diff
                        update_query = "UPDATE {} SET leave_count = %s WHERE employee_id = %s;"
                        cursor.execute(update_query.format(company_name), (leave_count, employee_id))
                        cnx.commit()
                        cursor.close()
                        cnx.close()

                        messages.success(request,'leave applied successfully')
                        return redirect('/')
                    else:
                        cursor.close()
                        cnx.close()
                        messages.warning(request,'leave application already exist for selected date range')
                        return redirect('/')
                else:
                    cursor.close()
                    cnx.close()
                    messages.warning(request,'employee not found')
                    return redirect('/company/logout')
            except Exception as e:
                messages.warning(request,e)
                return redirect('/')
        else:
            return render (request,'leave.html')
    else:
        messages.warning(request,'please login to apply leave')
        return redirect('/company/login')
