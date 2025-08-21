from django import forms
from django.contrib.auth.models import User
from .models import Booking, Passenger


class BookingForm(forms.ModelForm):
    """Form for booking travel options"""
    
    class Meta:
        model = Booking
        fields = ['number_of_seats', 'billing_name', 'billing_street_address', 
                 'billing_city', 'billing_pin_code', 'billing_country']
        widgets = {
            'number_of_seats': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10',
                'placeholder': 'Number of passengers'
            }),
            'billing_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name for billing'
            }),
            'billing_street_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street address'
            }),
            'billing_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'billing_pin_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'PIN code'
            }),
            'billing_country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
        }


class PassengerForm(forms.ModelForm):
    """Form for individual passenger details"""
    
    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'age', 'gender']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '120',
                'placeholder': 'Age'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


# Dynamic formset for multiple passengers
PassengerFormSet = forms.formset_factory(
    PassengerForm,
    extra=1,
    min_num=1,
    max_num=10,
    validate_min=True,
    validate_max=True
)
