from django import forms
from django.forms import ModelForm
from .models import Product,CustomUser
from django.contrib.auth.forms import UserCreationForm

class ProductForm(forms.ModelForm):
    name = forms.CharField(
        required=True,
        max_length=250,
        min_length=8,
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Nombre producto:',
            'id':'name'
        }),
        label="Nombre producto:"
    )

    description = forms.CharField(
        required=True,
        max_length=250,
        min_length=8,
        widget=forms.Textarea(attrs={
            'class':'form-control',
            'placeholder':'Descripcion producto:',
            'id':'description'
        }),
        label="Descripcion producto:"
    )

    price = forms.IntegerField(
        required=True,
        max_value=9999999,
        min_value=1,
        widget=forms.IntegerField(),
        label="Precio producto:"
    )

    image = forms.URLField(
    required=True,
    widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://ejemplo.com/imagen.jpg',
        'id': 'image'
    }),
    label="Imagen producto:"
    )

    class Meta:
        model = Product
        fields = ('name','description','price','image')
        




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