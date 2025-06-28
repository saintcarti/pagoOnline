from django import forms
from django.forms import ModelForm
from .models import Product,CustomUser,Category,Brand
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
        max_length=999,
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
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Precio en pesos chilenos',
            'id': 'price'
        }),
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
    
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'brand'
        }),
        label="Marca:"
    )
    
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'id': 'categories'
        }),
        label="Categorías:"
    )

    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'image', 'brand', 'categories')
        




class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu apellido'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com'
        })
    )
    rut = forms.CharField(
        max_length=12, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12.345.678-9'
        }),
        help_text='Formato: 12.345.678-9'
    )
    telefono = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678'
        }),
        help_text='Incluye código de país (+56)'
    )
    direccion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Calle, número, comuna, región...'
        }),
        help_text='Dirección completa de entrega'
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'rut', 'telefono', 'direccion')
        
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if rut:
            # Remover puntos y guión para validación
            rut_clean = rut.replace('.', '').replace('-', '')
            if len(rut_clean) < 8 or len(rut_clean) > 9:
                raise forms.ValidationError('El RUT debe tener entre 8 y 9 caracteres.')
        return rut
        
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Remover espacios y caracteres especiales para validación
            telefono_clean = telefono.replace(' ', '').replace('+', '').replace('-', '')
            if len(telefono_clean) < 8:
                raise forms.ValidationError('El teléfono debe tener al menos 8 dígitos.')
        return telefono

class StaffRegistrationForm(UserCreationForm):
    ROLES = (
        ('bodeguero', 'Bodeguero'),
        ('contador', 'Contador'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del usuario'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido del usuario'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@empresa.com'
        })
    )
    rol = forms.ChoiceField(
        choices=ROLES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    rut = forms.CharField(
        max_length=12, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12.345.678-9'
        })
    )
    telefono = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678'
        })
    )
    direccion = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Dirección completa del usuario'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'rol', 'rut', 'telefono', 'direccion', 'is_active')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a los campos heredados
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'nombre_usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña segura'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme la contraseña'
        })
        self.fields['is_active'].widget.attrs.update({
            'class': 'form-check-input'
        })

class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'rol', 'rut', 'telefono', 'direccion', 'is_active']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }