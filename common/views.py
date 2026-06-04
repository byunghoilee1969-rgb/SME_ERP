from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Supplier, Item
from .forms import SupplierForm, ItemForm


class SupplierListView(ListView):
    model = Supplier
    template_name = 'common/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        active = self.request.GET.get('active', '')
        if active == '1':
            qs = qs.filter(is_active=True)
        elif active == '0':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['active'] = self.request.GET.get('active', '')
        return ctx


class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'common/supplier_form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        messages.success(self.request, '공급업체가 등록되었습니다.')
        return super().form_valid(form)


class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'common/supplier_form.html'
    success_url = reverse_lazy('supplier_list')

    def form_valid(self, form):
        messages.success(self.request, '공급업체 정보가 수정되었습니다.')
        return super().form_valid(form)


class ItemListView(ListView):
    model = Item
    template_name = 'common/item_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(code__icontains=q)
        category = self.request.GET.get('category', '')
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        ctx['category'] = self.request.GET.get('category', '')
        ctx['categories'] = Item.CATEGORY_CHOICES
        return ctx


class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    template_name = 'common/item_form.html'
    success_url = reverse_lazy('item_list')

    def form_valid(self, form):
        messages.success(self.request, '품목이 등록되었습니다.')
        return super().form_valid(form)


class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'common/item_form.html'
    success_url = reverse_lazy('item_list')

    def form_valid(self, form):
        messages.success(self.request, '품목 정보가 수정되었습니다.')
        return super().form_valid(form)
