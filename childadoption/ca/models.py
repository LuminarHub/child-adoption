from django.db import models
from django import forms
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    user_type_choices = [ 
        ('Admin', 'Admin'),
        ('User', 'User'),
    ]
    user_type = models.CharField(max_length=50, choices=user_type_choices, default='User') 
    is_organization = models.BooleanField(default=False)

class SuperAdmin(CustomUser):
    is_available = models.BooleanField(default=True)

class UserCust(CustomUser):
    GENDER_CHOICES = (('male', 'Male'),('female', 'Female'),('other', 'Other'))
    fname=models.CharField(max_length=50,null=True)
    lname=models.CharField(max_length=50,null=True)
    emailaddress=models.EmailField(max_length=254,null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    location= models.CharField(max_length=30)
    addresss=models.TextField()
    phone_number=models.CharField(max_length=10)


class Organization(models.Model):
    user = models.OneToOneField(UserCust, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='organization')
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return self.name
class Donation(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    personal_details = models.ForeignKey(UserCust, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(null=True, blank=True)
    category_choices = [
        ('medical', 'Medical'),
        ('clothings', 'Clothings'),
        ('education', 'Education'),
        ('sports', 'Sports'),
        ('food_and_nutrition', 'Food and Nutrition'),
    ]
    category = models.CharField(max_length=50, choices=category_choices, default='medical') 
    order_id = models.CharField(max_length=100, blank=True, null=True)  # Razorpay Order ID
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Razorpay Payment ID
    status = models.CharField(max_length=20, default='pending')  # Payment Status
    is_paid = models.BooleanField(default=False,blank=True,null=True)

    def __str__(self):
        return f"{self.personal_details} - {self.organization} - {self.amount} - {self.category}"

    

class AdoptionRequest(models.Model):
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,null=True)
    personal_details=models.ForeignKey(UserCust,on_delete=models.CASCADE)
    subject=models.CharField(max_length=150)
    s_op =(('A','Approved'),
                  ('R','Rejected'),
                  ('P','Pending'))
    status=models.CharField(max_length=50,null=True,blank=True,choices=s_op,default='P')
    full_name = models.CharField(max_length=100,blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15,blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=[('single', 'Single'), ('married', 'Married'), ('divorced', 'Divorced'), ('widowed', 'Widowed')],blank=True, null=True)
    occupation = models.CharField(max_length=100,blank=True, null=True)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    cri_options =(('Yes','Yes'),
                  ('No','No'),)
    criminal_history = models.CharField(max_length=100,null=True,blank=True,choices=cri_options)
    id_proof = models.FileField(upload_to='id_proof/',null=True,blank=True)  # New field for ID proof file
    additional_comments = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    

class ChildDetails(models.Model):
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,null=True)
    name=models.CharField(max_length=50)
    age=models.CharField(max_length=50)
    image = models.ImageField(upload_to='child')
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES,null=True)
    since=models.PositiveIntegerField()
    blood_group = models.CharField(max_length=50,null=True,blank=True)
    education = models.CharField(max_length=200,null=True,blank=True)
    def __str__(self):
        return f"{self.name} ---- {self.organization.name}"


class ChildAppointment(models.Model):
    user = models.ForeignKey(UserCust, on_delete=models.CASCADE, null=True, blank=True)
    child = models.ForeignKey(ChildDetails, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"Appointment for {self.user} on {self.date} at {self.time}"
        

class SponserShipApplicants(models.Model):
    child = models.ForeignKey('ChildDetails', on_delete=models.CASCADE, null=True, blank=True)
    
    SPONSOR_TYPES = (
        ('medical', 'Medical'),
        ('clothings', 'Clothings'),
        ('education', 'Education'),
        ('sports', 'Sports'),
        ('food_and_nutrition', 'Food and Nutrition'),
    )
    sponsor_category = models.CharField(max_length=20, choices=SPONSOR_TYPES, null=True, blank=True)
    amount = models.PositiveIntegerField(default=100,null=True)
    is_paid = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"{self.child} - "
    
class LifeTimeSponserShip(models.Model):
    child =  models.ForeignKey(ChildDetails,on_delete=models.CASCADE)
    sponser =  models.ForeignKey(UserCust,on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()
    def __str__(self):
      return f"Sponsorship for {self.child} by {self.sponser} from {self.date_from} to {self.date_to}"



        
class LifeTimeSponserShipNeeds(models.Model):
    SPONSOR_TYPES = (
        ('medical', 'Medical'),
        ('clothings', 'Clothings'),
        ('education', 'Education'),
        ('sports', 'Sports'),
        ('food_and_nutrition', 'Food and Nutrition'),
    )
    sponsor_type = models.CharField(max_length=20, choices=SPONSOR_TYPES, null=True)
    lifeTimesponserShip = models.ForeignKey(LifeTimeSponserShip,on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    is_paid = models.BooleanField(default=False)
    description = models.CharField(max_length=1000,null=True,blank=True)

    

    




    


    
    
    
    



@receiver(post_save, sender=Organization)
def update_is_organization(sender, instance, created, **kwargs):
    if created:
        instance.user.is_organization = True
        instance.user.save()




