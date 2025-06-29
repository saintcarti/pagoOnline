from django import forms
from django.forms import ModelForm
from .models import Product,CustomUser,Category,Brand,Order,OrderItem,Order,OrderItem
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
            'placeholder': 'Calle, número, comuna...'
        }),
        help_text='Dirección sin incluir ciudad'
    )
    ciudad = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Santiago, Valparaíso, Concepción...'
        }),
        help_text='Ciudad donde vives'
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'rut', 'telefono', 'direccion', 'ciudad')
        
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
            'placeholder': 'Dirección del usuario'
        })
    )
    ciudad = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ciudad del usuario'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'rol', 'rut', 'telefono', 'direccion', 'ciudad', 'is_active')
        
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
        fields = ['username', 'email', 'first_name', 'last_name', 'rol', 'rut', 'telefono', 'direccion', 'ciudad', 'is_active']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 3}),
        }


# Formularios para órdenes

class ManualOrderForm(forms.ModelForm):
    """Formulario para crear órdenes manuales por vendedores"""
    
    class Meta:
        model = Order
        fields = [
            'user', 'order_type', 'payment_status', 'shipping_address', 
            'shipping_city', 'shipping_phone', 'notes'
        ]
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'order_type': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales sobre la orden...'}),
        }
        labels = {
            'user': 'Cliente',
            'order_type': 'Tipo de Orden',
            'payment_status': 'Estado de Pago',
            'shipping_address': 'Dirección de Envío',
            'shipping_city': 'Ciudad',
            'shipping_phone': 'Teléfono de Contacto',
            'notes': 'Notas Adicionales',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo usuarios activos para el campo user
        self.fields['user'].queryset = CustomUser.objects.filter(is_active=True).order_by('first_name', 'last_name')
        self.fields['user'].empty_label = "Seleccionar cliente..."


class OrderStatusUpdateForm(forms.ModelForm):
    """Formulario para actualizar el estado de una orden"""
    
    class Meta:
        model = Order
        fields = ['order_status', 'payment_status', 'tracking_number', 'estimated_delivery', 'notes']
        widgets = {
            'order_status': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'tracking_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de seguimiento...'}),
            'estimated_delivery': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'order_status': 'Estado de la Orden',
            'payment_status': 'Estado de Pago',
            'tracking_number': 'Número de Seguimiento',
            'estimated_delivery': 'Entrega Estimada',
            'notes': 'Notas',
        }


class OrderItemForm(forms.ModelForm):
    """Formulario para agregar items a una orden"""
    
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'product': 'Producto',
            'quantity': 'Cantidad',
            'price': 'Precio Unitario',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos con stock disponible
        self.fields['product'].queryset = Product.objects.filter(stock__gt=0).order_by('name')
        self.fields['product'].empty_label = "Seleccionar producto..."