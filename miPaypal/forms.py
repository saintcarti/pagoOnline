from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio': forms.NumberInput(attrs={'step': '0.01'}),
        }