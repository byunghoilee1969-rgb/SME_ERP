from django import forms
from django.forms import inlineformset_factory
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem
import datetime


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['supplier', 'order_date', 'expected_date', 'notes']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'order_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'supplier': '공급업체',
            'order_date': '발주일',
            'expected_date': '납기예정일',
            'notes': '비고',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields['order_date'].initial = datetime.date.today()


class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['item', 'quantity', 'unit_price']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-select item-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.001', 'min': '0'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control price-input', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'item': '품목',
            'quantity': '수량',
            'unit_price': '단가',
        }


PurchaseOrderItemFormSet = inlineformset_factory(
    PurchaseOrder,
    PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=1,
    can_delete=True,
    fields=['item', 'quantity', 'unit_price'],
)


class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = ['purchase_order', 'receipt_date', 'warehouse', 'notes']
        widgets = {
            'purchase_order': forms.Select(attrs={'class': 'form-select'}),
            'receipt_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warehouse': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'purchase_order': '발주번호',
            'receipt_date': '입고일',
            'warehouse': '창고',
            'notes': '비고',
        }

    def __init__(self, *args, **kwargs):
        order_pk = kwargs.pop('order_pk', None)
        super().__init__(*args, **kwargs)
        from .models import PurchaseOrder
        self.fields['purchase_order'].queryset = PurchaseOrder.objects.filter(
            status__in=['CONFIRMED', 'PARTIAL']
        )
        if order_pk:
            self.fields['purchase_order'].initial = order_pk
        if not self.instance.pk:
            self.fields['receipt_date'].initial = datetime.date.today()


class GoodsReceiptItemForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptItem
        fields = ['order_item', 'quantity_received', 'notes']
        widgets = {
            'order_item': forms.Select(attrs={'class': 'form-select'}),
            'quantity_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'order_item': '발주품목',
            'quantity_received': '입고수량',
            'notes': '비고',
        }


GoodsReceiptItemFormSet = inlineformset_factory(
    GoodsReceipt,
    GoodsReceiptItem,
    form=GoodsReceiptItemForm,
    extra=1,
    can_delete=True,
    fields=['order_item', 'quantity_received', 'notes'],
)
