from django.shortcuts import render,redirect
import mysql.connector
from company.models import Company,Branches
import matplotlib.pyplot as plt
import numpy as np
import datetime
from io import BytesIO
from PIL import Image
import base64,urllib
from django.contrib import auth,messages
# Create your views here.
def home(request):
    
    return render(request,'index.html')
def leave_dashboard(request):
    if 'employee_id' in request.session:
        company_name=request.session['company_name']
        context={}
        cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
        cursor = cnx.cursor()
        get_leave="select * from "+company_name+"_leaves where employee_id='"+request.session['employee_id']+"' order by to_date desc"
        cursor.execute(get_leave)
        my_leaves=cursor.fetchall()
        used_leaves="select datediff(to_date,from_date)+1  from "+ company_name+"_leaves where employee_id='"+request.session['employee_id']+"' and (status='applied' or status='approved')"
        cursor.execute(used_leaves)
        used_leaves_counts=cursor.fetchall()
        used_leaves_count=0
        for value in used_leaves_counts:
            used_leaves_count+=value[0]
        context['used_leaves']=used_leaves_count
        leaves_remaining="select leave_count from "+ company_name+" where employee_id='"+request.session['employee_id']+"'"
        cursor.execute(leaves_remaining)
        leaves_remaining_count=cursor.fetchone()
        context['remaining_leaves']=leaves_remaining_count[0]
        reporting_employee_query="select employee_id from "+company_name+" where reports_to='"+request.session['employee_id']+"'"
        cursor.execute(reporting_employee_query)
        reporting_employees=cursor.fetchall()
        fig, ax = plt.subplots()
        size_of_groups=[used_leaves_count,leaves_remaining_count[0]]
        names=[str(used_leaves_count)+' days',str(leaves_remaining_count[0])+' days']
        ax.pie(size_of_groups,labels=names,labeldistance=0.9, textprops={'fontsize': 14})
        # add a circle at the center to transform it in a donut chart
        my_circle=plt.Circle( (0,0), 0.7, color='white')
        p=plt.gcf()
        p.gca().add_artist(my_circle)
        p.patch.set_facecolor('none')
        total_leaves = np.sum(size_of_groups)
        ax.text(0, 0, total_leaves, ha='center', va='center', fontsize=18)
       
        # Set legend
        labels = ['Used Leaves', 'Leaves Remaining']
        plt.legend(labels, loc='upper right',bbox_to_anchor=(1.4, 0.9),fontsize=11)

        # Set title
        plt.title('Leaves Usage Chart',fontsize=15)
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        pie = base64.b64encode(image_png)
        pie = pie.decode('utf-8')
        context = {'pie': pie}
        if len(reporting_employees)>0:
            rep_list=[]
            for reporting_employee in reporting_employees:
                rep_list.append(reporting_employee[0])
            rep_list = tuple(rep_list) if len(rep_list) > 1 else f"('{rep_list[0]}')"
            
            leaves_toapprove_query="select * from "+company_name+"_leaves where status='applied' and employee_id IN {}".format(rep_list)
            
            cursor.execute(leaves_toapprove_query)
            leaves_toapprove=cursor.fetchall()
            context['leaves_toapprove']=leaves_toapprove
        context['my_leaves']=my_leaves
        return render(request,'leave_dashboard.html',context)
    else:
        messages.warning(request,'please login to view leaves')
        return redirect('/company/login')

def process_leave(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        employee_id=request.POST['employee_id']
        branch_id=request.POST['branch_id']
        from_date=request.POST['from_date']
        
        to_date=request.POST['to_date']
        leave_type=request.POST['leave_type']
        company_name=request.session['company_name']
        try:
            cnx = mysql.connector.connect(user='root', password='Mohan_1997', host='localhost', database='employee')
            cursor = cnx.cursor()
            query="update {} set status=%s where employee_id=%s and branch_id=%s and  from_date=STR_TO_DATE(%s, '%M %e, %Y') and to_date=STR_TO_DATE(%s, '%M %e, %Y') and leave_type=%s"
            table=company_name+'_leaves'
            if action == 'approve':
                cursor.execute(query.format(table),('approved',employee_id,branch_id,from_date,to_date,leave_type))
                cnx.commit()
                cursor.close()
                cnx.close()
                return redirect('leave_dashboard')
            elif action == 'reject':
                cursor.execute(query.format(table),('rejected',employee_id,branch_id,from_date,to_date,leave_type))
                cnx.commit()
                
                from_date_obj = datetime.datetime.strptime(from_date, '%B %d, %Y')
                to_date_obj = datetime.datetime.strptime(to_date, '%B %d, %Y')
                            
                # Calculate the difference in days
                date_diff = (to_date_obj - from_date_obj).days+1
                check_employee="select * from "+company_name+" where employee_id="+"'"+employee_id+"'"
                cursor.execute(check_employee)
                employee=cursor.fetchone()
                leave_balance=employee[26]
                leave_count=leave_balance+date_diff
                update_query = "UPDATE {} SET leave_count = %s WHERE employee_id = %s;"
                cursor.execute(update_query.format(company_name), (leave_count, employee_id))
                cnx.commit()
                cursor.close()
                cnx.close()
                return redirect('leave_dashboard')
        except Exception as e:
            messages.warning(request,e)
            return redirect('/')
    else:
        return redirect('/leave_dashboard')