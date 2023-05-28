from django.db import models



class Company(models.Model):
    company_id=models.CharField(max_length=50,primary_key=True,null=False,blank=False)
    company_name = models.CharField(max_length=50,unique=True,null=False,blank=False)
    founder = models.CharField(max_length=50,null=False,blank=False)
    established_date = models.DateField()
    company_contact = models.CharField( max_length=12,null=False,blank=False)
    company_mail = models.EmailField(unique=True,null=False,blank=False)
    company_password=models.CharField(max_length=255)
    company_url=models.URLField(unique=True,null=False,blank=False)
    

class Branches(models.Model):
    
    Branch_id=models.CharField(max_length=50,null=False,blank=False)
    Branch_name = models.CharField(max_length=50,null=False,blank=False)
    Branch_lat = models.FloatField()
    Branch_long = models.FloatField()
    Branch_range = models.IntegerField()
    is_main=models.BooleanField(default=False)
    company=models.ForeignKey(Company,on_delete=models.CASCADE)
    class Meta:
        unique_together = [("Branch_id","company")]
        index_together = [("Branch_id","company")]