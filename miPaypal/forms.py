from django import forms
from .models import Product,CustomUser
from django.contrib.auth.forms import UserCreationForm

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
        }

class CustomUserCreationForm(UserCreationForm):
    rut = forms.CharField(max_length=12, required=True)
    telefono = forms.CharField(max_length=15, required=True)
    direccion = forms.CharField(widget=forms.Textarea, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'rut', 'telefono', 'direccion')

class StaffRegistrationForm(UserCreationForm):
    ROLES = (
        ('bodeguero', 'Bodeguero'),
        ('contador', 'Contador'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    )
    
    rol = forms.ChoiceField(choices=ROLES)
    rut = forms.CharField(max_length=12, required=True)
    telefono = forms.CharField(max_length=15, required=True)
    direccion = forms.CharField(widget=forms.Textarea, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'rol', 'rut', 'telefono', 'direccion')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'rol', 'rut', 'telefono', 'direccion', 'is_active']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }