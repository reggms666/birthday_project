# friends/forms.py
from django import forms
from .models import Friend
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['name', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'})
        }