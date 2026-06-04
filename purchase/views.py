from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from .models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem
from .forms import (PurchaseOrderForm, PurchaseOrderItemFormSet,
                    GoodsReceiptForm, GoodsReceiptItemFormSet)
from common.models import Supplier, Item
import datetime


class DashboardView(View):
    def get(self, request):
        today = timezone.now().date()
        month_start = today.replace(day=1)

        order_stats = {
            'draft': PurchaseOrder.objects.filter(status='DRAFT').count(),
            'confirmed': PurchaseOrder.objects.filter(status='CONFIRMED').count(),
            'partial': PurchaseOrder.objects.filter(status='PARTIAL').count(),
            'completed': PurchaseOrder.objects.filter(status='COMPLETED').count(),
            'this_month': PurchaseOrder.objects.filter(order_date__gte=month_start).count(),
        }
        receipt_stats = {
            'this_month': GoodsReceipt.objects.filter(receipt_date__gte=month_start).count(),
            'pending': GoodsReceipt.objects.filter(status='PENDING').count(),
            'completed': GoodsReceipt.objects.filter(status='COMPLETED').count(),
        }
        recent_orders = PurchaseOrder.objects.select_related('supplier').order_by('-created_at')[:5]
        recent_receipts = GoodsReceipt.objects.select_related('purchase_order').order_by('-created_at')[:5]

        return render(request, 'dashboard.html', {
            'order_stats': order_stats,
            'receipt_stats': receipt_stats,
            'recent_orders': recent_orders,
            'recent_receipts': recent_receipts,
        })


class PurchaseOrderListView(ListView):
    model = PurchaseOrder
    template_name = 'purchase/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        qs = PurchaseOrder.objects.select_related('supplier').order_by('-created_at')
        status = self.request.GET.get('status', '')
        supplier = self.request.GET.get('supplier', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        q = self.request.GET.get('q', '')
        if status:
            qs = qs.filter(status=status)
        if supplier:
            qs = qs.filter(supplier_id=supplier)
        if date_from:
            qs = qs.filter(order_date__gte=date_from)
        if date_to:
            qs = qs.filter(order_date__lte=date_to)
        if q:
            qs = qs.filter(order_no__icontains=q) | qs.filter(supplier__name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['suppliers'] = Supplier.objects.filter(is_active=True)
        ctx['status_choices'] = PurchaseOrder.STATUS_CHOICES
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_supplier'] = self.request.GET.get('supplier', '')
        ctx['date_from'] = self.request.GET.get('date_from', '')
        ctx['date_to'] = self.request.GET.get('date_to', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class PurchaseOrderCreateView(View):
    template_name = 'purchase/order_form.html'

    def get(self, request):
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet()
        return render(request, self.template_name, {'form': form, 'formset': formset, 'title': '발주 등록'})

    def post(self, request):
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                if request.user.is_authenticated:
                    order.created_by = request.user
                order.save()
                formset.instance = order
                formset.save()
                order.update_total_amount()
            messages.success(request, f'발주 {order.order_no}이(가) 등록되었습니다.')
            return redirect('order_detail', pk=order.pk)
        return render(request, self.template_name, {'form': form, 'formset': formset, 'title': '발주 등록'})


class PurchaseOrderDetailView(DetailView):
    model = PurchaseOrder
    template_name = 'purchase/order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.object.items.select_related('item').all()
        ctx['receipts'] = self.object.receipts.order_by('-created_at')
        return ctx


class PurchaseOrderUpdateView(View):
    template_name = 'purchase/order_form.html'

    def get(self, request, pk):
        order = get_object_or_404(PurchaseOrder, pk=pk)
        if order.status != 'DRAFT':
            messages.error(request, '초안 상태의 발주만 수정할 수 있습니다.')
            return redirect('order_detail', pk=pk)
        form = PurchaseOrderForm(instance=order)
        formset = PurchaseOrderItemFormSet(instance=order)
        return render(request, self.template_name, {
            'form': form, 'formset': formset,
            'title': '발주 수정', 'order': order
        })

    def post(self, request, pk):
        order = get_object_or_404(PurchaseOrder, pk=pk)
        if order.status != 'DRAFT':
            messages.error(request, '초안 상태의 발주만 수정할 수 있습니다.')
            return redirect('order_detail', pk=pk)
        form = PurchaseOrderForm(request.POST, instance=order)
        formset = PurchaseOrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save()
                formset.save()
                order.update_total_amount()
            messages.success(request, '발주가 수정되었습니다.')
            return redirect('order_detail', pk=order.pk)
        return render(request, self.template_name, {
            'form': form, 'formset': formset,
            'title': '발주 수정', 'order': order
        })


class PurchaseOrderConfirmView(View):
    def post(self, request, pk):
        order = get_object_or_404(PurchaseOrder, pk=pk)
        if order.status != 'DRAFT':
            messages.error(request, '초안 상태의 발주만 확정할 수 있습니다.')
        elif not order.items.exists():
            messages.error(request, '발주 품목이 없습니다.')
        else:
            order.status = 'CONFIRMED'
            order.save(update_fields=['status'])
            messages.success(request, f'발주 {order.order_no}이(가) 확정되었습니다.')
        return redirect('order_detail', pk=pk)


class GoodsReceiptListView(ListView):
    model = GoodsReceipt
    template_name = 'purchase/receipt_list.html'
    context_object_name = 'receipts'
    paginate_by = 20

    def get_queryset(self):
        qs = GoodsReceipt.objects.select_related('purchase_order__supplier').order_by('-created_at')
        status = self.request.GET.get('status', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        q = self.request.GET.get('q', '')
        if status:
            qs = qs.filter(status=status)
        if date_from:
            qs = qs.filter(receipt_date__gte=date_from)
        if date_to:
            qs = qs.filter(receipt_date__lte=date_to)
        if q:
            qs = qs.filter(receipt_no__icontains=q) | qs.filter(purchase_order__order_no__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = GoodsReceipt.STATUS_CHOICES
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['date_from'] = self.request.GET.get('date_from', '')
        ctx['date_to'] = self.request.GET.get('date_to', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class GoodsReceiptCreateView(View):
    template_name = 'purchase/receipt_form.html'

    def get(self, request):
        order_pk = request.GET.get('order', None)
        form = GoodsReceiptForm(order_pk=order_pk)
        formset = GoodsReceiptItemFormSet()
        # Pre-populate formset if order is given
        order = None
        if order_pk:
            try:
                order = PurchaseOrder.objects.get(pk=order_pk, status__in=['CONFIRMED', 'PARTIAL'])
            except PurchaseOrder.DoesNotExist:
                pass
        return render(request, self.template_name, {
            'form': form, 'formset': formset, 'order': order, 'title': '입고 등록'
        })

    def post(self, request):
        form = GoodsReceiptForm(request.POST)
        formset = GoodsReceiptItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                receipt = form.save(commit=False)
                if request.user.is_authenticated:
                    receipt.created_by = request.user
                receipt.status = 'COMPLETED'
                receipt.save()
                formset.instance = receipt
                formset.save()
            messages.success(request, f'입고 {receipt.receipt_no}이(가) 등록되었습니다.')
            return redirect('receipt_detail', pk=receipt.pk)
        order_pk = request.POST.get('purchase_order')
        order = None
        if order_pk:
            try:
                order = PurchaseOrder.objects.get(pk=order_pk)
            except PurchaseOrder.DoesNotExist:
                pass
        return render(request, self.template_name, {
            'form': form, 'formset': formset, 'order': order, 'title': '입고 등록'
        })


class GoodsReceiptDetailView(DetailView):
    model = GoodsReceipt
    template_name = 'purchase/receipt_detail.html'
    context_object_name = 'receipt'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['items'] = self.object.items.select_related('order_item__item').all()
        return ctx


def get_order_items_ajax(request):
    """AJAX endpoint: return order items for a given order PK."""
    order_pk = request.GET.get('order_pk')
    if not order_pk:
        return JsonResponse({'items': []})
    try:
        order = PurchaseOrder.objects.get(pk=order_pk, status__in=['CONFIRMED', 'PARTIAL'])
    except PurchaseOrder.DoesNotExist:
        return JsonResponse({'items': []})
    items = []
    for oi in order.items.select_related('item').all():
        items.append({
            'id': oi.pk,
            'item_name': oi.item.name,
            'item_code': oi.item.code,
            'unit': oi.item.unit,
            'ordered_qty': str(oi.quantity),
            'received_qty': str(oi.received_quantity),
            'remaining_qty': str(oi.remaining_quantity),
        })
    return JsonResponse({'items': items})
