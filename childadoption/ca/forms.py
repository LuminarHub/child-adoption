from django import forms 
from ca.models import UserCust,ChildDetails,AdoptionRequest,ChildAppointment,Donation,LifeTimeSponserShip,LifeTimeSponserShipNeeds
from django.contrib.auth.forms import UserCreationForm
from datetime import date,timedelta

from django.core.exceptions import ValidationError

from datetime import date


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = UserCust
        fields=['fname','lname','emailaddress','gender','phone_number','location','addresss','username']
        
class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField()

class AdoptionRequestForm(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = [
            "subject", "full_name", "email", "phone", "address", 
            "age", "marital_status", "occupation", "income", 
            "criminal_history", "id_proof", "additional_comments"
        ]
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter address'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter age'}),
            'marital_status': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select marital status'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter occupation'}),
            'income': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter income'}),
            'criminal_history': forms.Select(attrs={'class': 'form-control'}),
            'id_proof': forms.FileInput(attrs={'class': 'form-control-file'}),
            'additional_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter additional comments'}),
        }

    def clean_age(self):
        age = self.cleaned_data['age']
        if age < 18:
            raise forms.ValidationError("Age must be 18 or older.")
        return age
    
class AdoptionRequestFormO(forms.ModelForm):
    class Meta:
        model = AdoptionRequest
        fields = [
        "status"
        ]
        widgets = {
            'status': forms.TextInput(attrs={'class': 'form-control'}),

        }



class ChildForm(forms.ModelForm):
    class Meta:
        model = ChildDetails
        fields = ['name', 'age', 'image', 'gender', 'since']
        widgets = {
    'name': forms.TextInput(attrs={'class': 'form-control '}),
    'age': forms.TextInput(attrs={'class': 'form-control'}),
    'image': forms.FileInput(attrs={'class': 'form-control'}),
    'gender': forms.TextInput(attrs={'class': 'form-control'}),
    'since': forms.TextInput(attrs={'class': 'form-control'}),
    
  
    
} 

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = UserCust
        fields = ['fname', 'lname', 'emailaddress', 'gender', 'phone_number', 'location','addresss' ]
        
    
class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ['organization', 'personal_details', 'category','amount']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount':forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
class ChildAppointmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Calculate tomorrow's date
        tomorrow = date.today() + timedelta(days=1)
        # Set the min attribute for the date field
        self.fields['date'].widget.attrs.update({'min': tomorrow.isoformat()})
    
    
    class Meta:
        model = ChildAppointment
        fields = ['user', 'date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class LifeTimeSponserShipForm(forms.ModelForm):
    class Meta:
        model = LifeTimeSponserShip
        fields = ['date_from', 'date_to']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')

        # Check if date_to is before date_from
        if date_to and date_to < date_from:
            self.add_error('date_to', 'End date cannot be before start date.')

        return cleaned_data
    

class LifeTimeSponserShipNeedsForm(forms.ModelForm):
    class Meta:
        model = LifeTimeSponserShipNeeds
        fields = ['sponsor_type', 'amount', 'description']

        widgets = {
            'sponsor_type': forms.Select(attrs={'class': 'form-control'}),
            'lifeTimesponserShip': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
