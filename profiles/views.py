from django.shortcuts import render,redirect,HttpResponse
from company.models import Company,Branches
from django.contrib import auth,messages
from django.contrib.auth import logout,authenticate, login
import mysql.connector
from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.mail import send_mail
from smtplib import SMTPAuthenticationError
import face_recognition
import pickle
import cv2
import re
import datetime
import numpy as np
import datetime
from PIL import Image
import base64,urllib
import matplotlib.pyplot as plt
from io import BytesIO
from tensorflow import keras
from tensorflow.keras.utils import img_to_array,array_to_img

# Create your views here.
def employee_profile(request,employee_id):
    if 'employee_id' in request.session or 'company_id' in request.session:
        employee=dict()
        cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
        cursor = cnx.cursor()
        company_name=request.session['company_name']
        
        query="select * from "+company_name+" where employee_id= '"+employee_id+"'"
        try:
            cursor.execute(query)
            employee_details=cursor.fetchone()
            cursor.close()
            cnx.close()
        except Exception as e:
            cursor.close()
            cnx.close()
            messages.warning(request,e)
            return redirect('/')
        try:
            if len(employee_details)>0:
                employee['employee_id']=employee_details[0]
                employee['branch_id']=employee_details[1]
                employee['fname']=employee_details[2]
                employee['lname']=employee_details[3]
                employee['email']=employee_details[4]
                employee['image']=employee_details[25]
                employee['designation']=employee_details[7]
                employee['reports_to']=employee_details[8]
                employee['mobile']=employee_details[11]
                employee['gender']=employee_details[12]
                employee['address']=employee_details[13]
                employee['dob']=employee_details[14]
                employee['blood_group']=employee_details[15]
                employee['father']=employee_details[16]
                employee['doj']=employee_details[17]
                employee['nationality']=employee_details[18]
                employee['marital_status']=employee_details[19]
                employee['religion']=employee_details[20]
                employee['pan']=employee_details[21]
                employee['education']=employee_details[22]
                employee['university']=employee_details[23]
                employee['disabled']=employee_details[24]
                image=pickle.loads(employee['image'])
                image=array_to_img(image)
                # Create a BytesIO object to hold the image data
                img_bytes = BytesIO()
                image.save(img_bytes, format='JPEG')
                img_bytes.seek(0)

                # Encode the image data as a base64 string
                img_data = base64.b64encode(img_bytes.getvalue()).decode()
                # Display the image in HTML
                html = f'<img src="data:image/jpeg;base64,{img_data}" alt="employee_image" class="rounded-circle" id="employee_image" width="150" height="150"/>'
                employee['image']=html

                company=Company.objects.get(company_name=request.session['company_name'])
                company_id=company.company_id
                # calculating Experience
                current_date=datetime.date.today()
                delta = current_date - employee['doj']
                
                years, months = divmod(delta.days, 365)
                months, days = divmod(months, 30)
                experience = {'years': years, 'months': months, 'days': days}
                employee['experience'] = experience
                branch=Branches.objects.get(Branch_id=employee['branch_id'],company_id=company_id)
                branch_name=branch.Branch_name
                employee['branch_name']=branch_name
                return render(request,'employee_profile.html',{'employee':employee})
            else:
                messages.warning(request,'something went wrong, please try again')
                return redirect('/')
        except Exception as e:
            messages.warning(request,'Employee does not exist')
            return redirect('/')
        
    else:
        messages.warning(request,'Please login to view your profile')
        return redirect('/company/login')

def company_profile(request):
    if 'company_id' in request.session:
        company=dict()
        
        branches=[]
        cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
        cursor = cnx.cursor()
        company_name=request.session['company_name']
        company_id=request.session['company_id']
        employee_count="select count(*) from "+company_name
        try:
            company_details=Company.objects.get(company_id=company_id)
            company["company_name"]=company_details.company_name
            company["company_id"]=company_details.company_id
            company["founder"]=company_details.founder
            company["established"]=company_details.established_date
            company["mobile"]=company_details.company_contact
            company["email"]=company_details.company_mail
            company["url"]=company_details.company_url
            company["branch_count"]=Branches.objects.filter(company_id=company_id).count()
            for i in range(0,company["branch_count"]):
                branch=dict()
                
                
                branch_details=Branches.objects.get(company_id=company_id,Branch_id='B'+str(i+1))
                branch["branch_id"]=branch_details.Branch_id
                
                branch["branch_name"]=branch_details.Branch_name
                branch["branch_area"]=branch_details.Branch_range
                branch["branch_location"]= 'lat :'+str(branch_details.Branch_lat)+' long :'+str(branch_details.Branch_long)
                query="select count(*) from "+company_name+" where branch_id= '"+branch["branch_id"]+"'"
                
                cursor.execute(query)
                branch["employee_count"]=cursor.fetchone()[0]
               
                branches.append(branch)
           
            cursor.execute(employee_count)
            company["employee_count"]=cursor.fetchone()[0]
            cursor.close()
            cnx.close()
            context={'company':company,'branches':branches}
            
            return render(request,'company_profile.html',context)
        except Exception as e:
            cursor.close()
            cnx.close()
            messages.warning(request,e)
            return redirect('/')
       
            
        
    else:
        messages.warning(request,'Please login to view your profile')
        return redirect('/company/company_login')
    
def employee_dashboard(request):
    if 'employee_id' in request.session:
        
        
        try:
            context={}
            employee_id=request.session['employee_id']
            company_name=request.session['company_name']
            cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
            cursor = cnx.cursor()
            

            current_month = datetime.datetime.now().strftime("%m")

            
            query ="select substring(date,9,2),TIMESTAMPDIFF(HOUR, logged_in, logged_out) as work_hours from "+company_name+"_attendance where employee_id= '"+employee_id+"' and logged_out is not null and substring(date,6,2)='"+current_month+"' order by substring(date,9,2)"
            cursor.execute(query)
            employee_details=cursor.fetchall()
            count=len(employee_details)
            if count>0:
                dates=[]
                hours=[]
                for i in range(0,count):
                    dates.append(str(employee_details[i][0]))
                    hours.append(employee_details[i][1])
                
                fig1, ax1 = plt.subplots()
                
                ax1.plot(dates,hours,color='green')
                plt.xlim(0,dates[-1])
                plt.ylim(0, 10)
                # Add labels and a title
                plt.xlabel('Day of Month')
                plt.ylabel('Working Hours')
                plt.title('Line chart of current month Working hours')
                ax1.set_facecolor('#F6F7C1')
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()
                line = base64.b64encode(image_png)
                line = line.decode('utf-8')
                context['line']=line
            else:
                dates=[]
                hours=[]
                fig1, ax1 = plt.subplots()
                
                ax1.plot(dates,hours,color='green')
                plt.xlim(0,5)
                plt.ylim(0, 10)
                # Add labels and a title
                plt.xlabel('Day of Month')
                plt.ylabel('Working Hours')
                plt.title('Line chart of current month Working hours')
                ax1.set_facecolor('#F6F7C1')
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()
                line = base64.b64encode(image_png)
                line = line.decode('utf-8')
                context['line']=line
            bar_query="""select DISTINCT substring(date,1,7),SUM(TIMESTAMPDIFF(HOUR, logged_in, logged_out))/count(*) as avg_hours  from """+company_name+"""_attendance 
            where employee_id='"""+employee_id+"""' and logged_out is not null  
            group by substring(date,1,7) order by substring(date,1,7) desc limit 5"""
            cursor.execute(bar_query)
            avg_hours=cursor.fetchall()
            count_avg=len(avg_hours)
            months=[]
            avg_hours_month=[]
            for i in range(0,count_avg):
                date_obj = datetime.datetime.strptime(str(avg_hours[i][0]), '%Y-%m')

                # Format the datetime object as a string in the desired format
                month_str = date_obj.strftime('%b')

                months.append(month_str)
                avg_hours_month.append(avg_hours[i][1])
            months.reverse()
            avg_hours_month.reverse()
            fig2, ax2 = plt.subplots()
            
            ax2.bar(months,avg_hours_month)
            plt.xlabel('Months')
            plt.ylabel('Avg Working Hours')
            plt.title('Month wise Avg Working hrs')
            ax2.set_facecolor('#F6F7C1')
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            bar = base64.b64encode(image_png)
            bar = bar.decode('utf-8')
            context['bar']=bar
            cursor.close()
            cnx.close()
            print(months)
            print(avg_hours_month)
            return render(request, 'employee_dashboard.html', context)
        except Exception as e:
            messages.warning(request,e)
            return redirect('/')
    else:
        messages.warning(request,'please login to view leaves')
        return redirect('/company/login')

def branch_profile(request,branch_id):
    if 'company_id' in request.session:
        branch_id=branch_id
        company_id=request.session['company_id']
        company_name=request.session['company_name']
        branch={}
        try:
            branch_details=Branches.objects.get(company_id=company_id,Branch_id=branch_id)
            branch["branch_id"]=branch_details.Branch_id
            branch["branch_name"]=branch_details.Branch_name
            
            branch["location"]='lat :'+str(branch_details.Branch_lat)+' long :'+str(branch_details.Branch_long)
           
            branch["branch_area"]=branch_details.Branch_range
            cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
            cursor = cnx.cursor()
            query="select count(*) from "+company_name+" where branch_id= '"+branch["branch_id"]+"'"
            cursor.execute(query)
            branch["employee_count"]=cursor.fetchone()[0]
            holidays="select * from "+company_name+"_"+branch_id+"_holidays"
            cursor.execute(holidays)
            data=cursor.fetchall()
            cursor.close()
            cnx.close()
            context={'branch':branch,'data':data}
            return render(request,'branch_profile.html',context)
        except Exception as e:
            messages.warning(request,e)
            return redirect('/')
    else:
        messages.warning(request,'Please login to view your profile')
        return redirect('/company/company_login')

def edit_employee(request,employee_id):
    if 'employee_id' in request.session or 'company_id' in request.session:
        if request.method=='POST':
            try:
                
                company_name=request.session["company_name"]
                cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                cursor = cnx.cursor()
                if 'employee_id' in request.session:
                    fetch_logged_in="select * from "+company_name+" where employee_id= '"+request.session['employee_id']+"'"
                    cursor.execute(fetch_logged_in)
                    logged_in_user=cursor.fetchone()
                fetch_employee="select * from "+company_name+" where employee_id= '"+employee_id+"'"
                cursor.execute(fetch_employee)
                employee=cursor.fetchone()
                cursor.close()
                cnx.close()
                branch_id=employee[1]
                designation=employee[7]
                reports_to=employee[8]
                is_root=employee[9]
                is_admin=employee[10]
                employee_fname=request.POST["employee_fname"]
                employee_lname=request.POST["employee_lname"]
                employee_mobile=request.POST["employee_mobile"]
                gender=request.POST["gender"]
                dob=request.POST["dob"]
                blood_group=request.POST["blood_group"]
                employee_father=request.POST["employee_father"]
                doj=request.POST["doj"]
                nationality=request.POST["nationality"]
                marital_status=request.POST["marital_status"]
                religion=request.POST["religion"]
                pan=request.POST["pan"]
                education=request.POST["education"]
                university=request.POST["university"]
                disabled=request.POST["disabled"]
                if disabled == 'yes':
                    disabled=1
                else:
                    disabled=0
                street=request.POST['street']
                city=request.POST['city']
                state=request.POST['state']
                pincode=request.POST['pincode']
                address=street+","+city+","+state+"-"+pincode
                if 'company_id' in request.session or logged_in_user[9]==1:
                    branch_id=request.POST["branch_id"]
                    designation=request.POST["designation"]
                    reports_to=request.POST["reports_to"]
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
                elif logged_in_user[10]==1:
                    branch_id=request.POST["branch_id"]
                    designation=request.POST["designation"]
                    reports_to=request.POST["reports_to"]
                        
                    is_admin=request.POST['admin']
                        
                    if is_admin=='yes':
                        is_admin=1
                    else:
                        is_admin=0
                if   'company_id' in request.session:
                    
                    
                    
                    cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                    cursor = cnx.cursor()
                     
                    update_query="UPDATE {} SET  branch_id=%s, first_name=%s, last_name=%s, designation=%s, reports_to=%s, is_root=%s, is_admin=%s, mobile=%s, gender=%s, address=%s, dob=%s, blood_group=%s, father_name=%s, doj=%s, nationality=%s, marital_status=%s, religion=%s, pan=%s, education=%s, university=%s, disabled=%s WHERE employee_id=%s;"
                    cursor.execute(update_query.format(company_name),( branch_id, employee_fname, employee_lname, designation, reports_to, is_root, is_admin, employee_mobile, gender, address, dob, blood_group, employee_father, doj, nationality, marital_status, religion, pan, education, university, disabled, employee_id))
                    cnx.commit()
                    cursor.close()
                    cnx.close()
                    return redirect('/profiles/employee_profile/'+employee_id)
                elif logged_in_user[0]==employee_id or logged_in_user[9]==1 or logged_in_user[10]==1:
                    cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
                    cursor = cnx.cursor()
                     
                    update_query="UPDATE {} SET  branch_id=%s, first_name=%s, last_name=%s, designation=%s, reports_to=%s, is_root=%s, is_admin=%s, mobile=%s, gender=%s, address=%s, dob=%s, blood_group=%s, father_name=%s, doj=%s, nationality=%s, marital_status=%s, religion=%s, pan=%s, education=%s, university=%s, disabled=%s WHERE employee_id=%s;"
                    cursor.execute(update_query.format(company_name),( branch_id, employee_fname, employee_lname, designation, reports_to, is_root, is_admin, employee_mobile, gender, address, dob, blood_group, employee_father, doj, nationality, marital_status, religion, pan, education, university, disabled, employee_id))
                    cnx.commit()
                    cursor.close()
                    cnx.close()
                    return redirect('/profiles/employee_profile/'+employee_id)


                else:
                    messages.warning(request,'you are not authorized to edit')
                    return redirect('/')
            except Exception as e:
                messages.warning(request,e)
                return redirect('/')
        else:
            company_name=request.session["company_name"]
            cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
            cursor = cnx.cursor()
            try:
                query1="select * from "+company_name+" where employee_id= '"+employee_id+"'"
                
                cursor.execute(query1)
                employee=cursor.fetchone()
                if 'employee_id' in request.session:
                    query2="select * from "+company_name+" where employee_id= '"+request.session['employee_id']+"'"
                    cursor.execute(query2)
                    searching_emplyee=cursor.fetchone()
                cursor.close()
                cnx.close()
                if  'company_id' in request.session:
                    my_list = re.split(r'[, -]', employee[13])
                    
                    address={}
                    address["street"]=my_list[0]
                    address["city"]=my_list[1]
                    address["state"]=my_list[2]
                    address["pincode"]=my_list[3]
                    context={'employee':employee,'address':address}
                    return render(request,'edit_employee.html',context)
                elif employee_id==request.session['employee_id'] or searching_emplyee[9]==1 or searching_emplyee[10]==1:
                    my_list = re.split(r'[, -]', employee[13])
                    
                    address={}
                    address["street"]=my_list[0]
                    address["city"]=my_list[1]
                    address["state"]=my_list[2]
                    address["pincode"]=my_list[3]
                    context={'employee':employee,'address':address}
                    return render(request,'edit_employee.html',context)
                else:
                    messages.warning(request,'you are not authorized to do the changes')
                    return redirect('/')
            except Exception as e:
                messages.warning(request,e)
                
                return redirect('/')
    else:
        messages.warning(request,'please login as company or employee to continue')
        return redirect('/')

def add_holiday(request,branch_id):
    if request.method=='POST':
        if 'company_id' in request.session:
            company_name=request.session['company_name']
            holiday_date=request.POST["holiday_date"]
            holiday_name=request.POST["holiday_name"]
            cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
            cursor = cnx.cursor()
            try:
                query="insert into "+company_name+"_"+branch_id+"_holidays (holiday_date,holiday_name) values (%s,%s)"
                cursor.execute(query,(holiday_date,holiday_name))
                cnx.commit()
                cursor.close()
                cnx.close()
                return redirect('/profiles/branches/'+branch_id)
            except Exception as e:
                messages.warning(request,e)
                return redirect('/')
        else:
            messages.warning(request,"please login to add holiday")
            return redirect('/company/company_login')
    else:
       return redirect('/') 


        