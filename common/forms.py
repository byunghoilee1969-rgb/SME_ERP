from django import forms
from .models import Supplier, Item


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['code', 'name', 'business_no', 'contact_person', 'phone', 'email', 'address', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_no': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'code': '공급업체코드',
            'name': '공급업체명',
            'business_no': '사업자번호',
            'contact_person': '담당자',
            'phone': '전화번호',
            'email': '이메일',
            'address': '주소',
            'is_active': '사용여부',
        }


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['code', 'name', 'category', 'unit', 'standard_price', 'description', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'standard_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'code': '품목코드',
            'name': '품목명',
            'category': '분류',
            'unit': '단위',
            'standard_price': '표준단가',
            'description': '설명',
            'is_active': '사용여부',
        }
