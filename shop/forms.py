import code
import os

from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from.models import Category, Product, RechargeLogs
from luis_carlos_cooperativa.utils.validators import validate_images
from luis_carlos_cooperativa.utils.convert_image import convert_image_to_webp


User = get_user_model()  


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
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    price = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )
    discount_percent = forms.IntegerField(
        required=False,
        min_value=0,
        max_value=99,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    offer_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    available = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 100:
            raise forms.ValidationError("El precio mínimo permitido es 100")
        return price
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            validate_images(image) 

            if image.name.lower().endswith(".webp"):
                return image

            converted = convert_image_to_webp(image, quality=20)
            if converted is None:
                raise forms.ValidationError("No se pudo convertir la imagen a WebP")

            new_image = ContentFile(converted.read())
            new_image.name = f"{image.name.rsplit('.', 1)[0]}.webp"
            return new_image
        return image

    def save(self, commit=True, seller=None, instance=None):
        data = self.cleaned_data
        if instance is None:
            product = Product(
                category=data['category'],
                name=data['name'],
                slug=slugify(data['name']),
                price=data['price'],
                description=data['description'],
                image=data['image'],
                seller=seller,
                discount_percent=data.get('discount_percent', 0),
                offer_active=data.get('offer_active', False),
                available=data.get('available', True)
            )
        else:
            product = instance
            product.category = data['category']
            product.name = data['name']
            product.slug = slugify(data['name'])
            product.price = data['price']
            product.description = data['description']
            if data['image']:
                product.image = data['image']
            product.seller = seller
            product.discount_percent = data.get('discount_percent', 0)
            product.offer_active = data.get('offer_active', False)
            product.available = data.get('available', True)
        if commit:
            product.save()
        return product

class CooperativeForm(forms.Form):
    cooperative_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de la cooperativa'
        })
    )
    cooperative_logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['cooperative_name'].initial = self.user.cooperative_name

    def save(self):
        if not self.user:
            raise ValueError("El formulario debe recibir el usuario para guardar los datos.")

        self.user.cooperative_name = self.cleaned_data['cooperative_name']

        new_logo = self.cleaned_data.get('cooperative_logo')
        if new_logo:
            old_logo = self.user.cooperative_logo
            if old_logo and hasattr(old_logo, 'path') and os.path.isfile(old_logo.path):
                os.remove(old_logo.path)

            self.user.cooperative_logo = new_logo

        self.user.save()
        return self.user




class CreditRechargeForm(forms.Form):
    code = forms.CharField(
        max_length=20,
        required=True,
        label="Código de verificación"
    )

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(50000)
        ],
        label="Monto a recargar"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']
        if not User.objects.filter(code=code).exists():
            raise forms.ValidationError("El código no corresponde a un usuario válido.")


        return code

    def save(self):
        code = self.cleaned_data.get('code')
        amount = self.cleaned_data.get('amount')

        if not code:
            raise ValueError("El formulario necesita un código válido.")

        try:
            user_obj = User.objects.get(code=code)
        except User.DoesNotExist:
            raise ValueError("El usuario con este código no existe.")

        user_obj.credit += amount
        user_obj.save()

        RechargeLogs.objects.create(
            seller=self.user,
            code=code,
            amount=amount,
        )

        return user_obj
