from django import forms
from.models import Category
from django.core.validators import MinValueValidator

PRODUCT_QUANTITY_CHOICES = [] # = [(1, "1"), (2, "2"), ..., (20, "20")]
for i in range(1, 21):
    PRODUCT_QUANTITY_CHOICES.append((i, str(i)))



class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int
    )

class CartUpdateProductForm(forms.Form):
    update = forms.IntegerField(
        max_value=20,
        min_value=1,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20, 'placeholder': 'Max 20'})
    )


class SubmitProductForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione una categoría"
    )
    name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre del producto', 'class': 'form-control'}),
    )
    price = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Precio', 'class': 'form-control'}),
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Descripción del producto', 'class': 'form-control', 'rows': 4}),
    )
    stock = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={'placeholder': 'Cantidad en stock', 'class': 'form-control'}),
    )
    image = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )
