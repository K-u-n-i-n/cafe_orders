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


OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    fields=('dish', 'quantity'),
    extra=1,
    widgets={
        'quantity': forms.NumberInput(attrs={'min': 1})
    }
)


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
