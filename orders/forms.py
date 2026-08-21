from django import forms

from .models import Order


class OrderCreateForm(forms.ModelForm):

    class Meta:
        model = Order

        fields = [
            'first_name',
            'phone',
            'address',
            'payment_method',
        ]

        widgets = {
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Введите ваше имя',
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '+998 90 123 45 67',
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Введите адрес доставки',
                }
            ),

            'payment_method': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
        }

        labels = {
            'first_name': 'Имя',
            'phone': 'Телефон',
            'address': 'Адрес доставки',
            'payment_method': 'Способ оплаты',
        }