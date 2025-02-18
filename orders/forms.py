from django import forms

from .models import Order, OrderItem


class OrderSearchForm(forms.Form):
    table_number = forms.IntegerField(required=False, label='Номер стола')
    status = forms.ChoiceField(
        choices=Order.ORDER_STATUS_CHOICES,
        required=False,
        label='Статус'
    )


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number']
        widgets = {
            'table_number': forms.NumberInput(attrs={'min': 1})
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ('dish', 'quantity')


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
