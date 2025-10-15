from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mobile Number',
            'type': 'tel'
        }),
        help_text='We need this for delivery updates'
    )
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone_number")


