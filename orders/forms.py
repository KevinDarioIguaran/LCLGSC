from django import forms


class SearchOrderForm(forms.Form):
    search_query = forms.CharField(
        required=True,
        max_length=250,
        widget=forms.TextInput(attrs={
            'placeholder': 'Escriba el nombre del producto que desea buscar en sus órdenes',
            'class': 'form-control'
        }),
        label=''
    )

