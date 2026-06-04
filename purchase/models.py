from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from common.models import Supplier, Item
import datetime


def generate_order_no():
    today = datetime.date.today().strftime('%Y%m%d')
    prefix = f'PO-{today}-'
    last = PurchaseOrder.objects.filter(order_no__startswith=prefix).order_by('-order_no').first()
    if last:
        try:
            seq = int(last.order_no.split('-')[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:04d}'


def generate_receipt_no():
    today = datetime.date.today().strftime('%Y%m%d')
    prefix = f'GR-{today}-'
    last = GoodsReceipt.objects.filter(receipt_no__startswith=prefix).order_by('-receipt_no').first()
    if last:
        try:
            seq = int(last.receipt_no.split('-')[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f'{prefix}{seq:04d}'


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', '초안'),
        ('CONFIRMED', '확정'),
        ('PARTIAL', '부분입고'),
        ('COMPLETED', '완료'),
        ('CANCELLED', '취소'),
    ]

    order_no = models.CharField(max_length=30, unique=True, verbose_name='발주번호')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='공급업체')
    order_date = models.DateField(verbose_name='발주일')
    expected_date = models.DateField(null=True, blank=True, verbose_name='납기예정일')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name='상태')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='총금액')
    notes = models.TextField(blank=True, verbose_name='비고')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='purchase_orders', verbose_name='등록자')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        verbose_name = '발주'
        verbose_name_plural = '발주 목록'
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = generate_order_no()
        super().save(*args, **kwargs)

    def update_total_amount(self):
        total = self.items.aggregate(total=Sum('amount'))['total'] or 0
        self.total_amount = total
        self.save(update_fields=['total_amount'])

    def update_status(self):
        items = self.items.all()
        if not items.exists():
            return
        total_qty = sum(i.quantity for i in items)
        total_received = sum(i.received_quantity for i in items)
        if total_received == 0:
            if self.status not in ('DRAFT', 'CANCELLED'):
                self.status = 'CONFIRMED'
        elif total_received < total_qty:
            self.status = 'PARTIAL'
        else:
            self.status = 'COMPLETED'
        self.save(update_fields=['status'])

    def get_status_badge_class(self):
        return {
            'DRAFT': 'secondary',
            'CONFIRMED': 'primary',
            'PARTIAL': 'warning',
            'COMPLETED': 'success',
            'CANCELLED': 'danger',
        }.get(self.status, 'secondary')


class PurchaseOrderItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items', verbose_name='발주')
    item = models.ForeignKey(Item, on_delete=models.PROTECT, verbose_name='품목')
    quantity = models.DecimalField(max_digits=15, decimal_places=3, verbose_name='발주수량')
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='단가')
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0, verbose_name='금액')
    received_quantity = models.DecimalField(max_digits=15, decimal_places=3, default=0, verbose_name='입고수량')

    class Meta:
        verbose_name = '발주품목'
        verbose_name_plural = '발주품목 목록'

    def __str__(self):
        return f'{self.order.order_no} - {self.item.name}'

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    @property
    def remaining_quantity(self):
        return self.quantity - self.received_quantity


class GoodsReceipt(models.Model):
    STATUS_CHOICES = [
        ('PENDING', '대기'),
        ('COMPLETED', '완료'),
        ('CANCELLED', '취소'),
    ]

    receipt_no = models.CharField(max_length=30, unique=True, verbose_name='입고번호')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.PROTECT,
                                       related_name='receipts', verbose_name='발주')
    receipt_date = models.DateField(verbose_name='입고일')
    warehouse = models.CharField(max_length=100, blank=True, verbose_name='창고')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name='상태')
    notes = models.TextField(blank=True, verbose_name='비고')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='goods_receipts', verbose_name='등록자')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')

    class Meta:
        verbose_name = '입고'
        verbose_name_plural = '입고 목록'
        ordering = ['-created_at']

    def __str__(self):
        return self.receipt_no

    def save(self, *args, **kwargs):
        if not self.receipt_no:
            self.receipt_no = generate_receipt_no()
        super().save(*args, **kwargs)

    def get_status_badge_class(self):
        return {
            'PENDING': 'warning',
            'COMPLETED': 'success',
            'CANCELLED': 'danger',
        }.get(self.status, 'secondary')


class GoodsReceiptItem(models.Model):
    receipt = models.ForeignKey(GoodsReceipt, on_delete=models.CASCADE, related_name='items', verbose_name='입고')
    order_item = models.ForeignKey(PurchaseOrderItem, on_delete=models.PROTECT,
                                   related_name='receipt_items', verbose_name='발주품목')
    quantity_received = models.DecimalField(max_digits=15, decimal_places=3, verbose_name='입고수량')
    notes = models.CharField(max_length=200, blank=True, verbose_name='비고')

    class Meta:
        verbose_name = '입고품목'
        verbose_name_plural = '입고품목 목록'

    def __str__(self):
        return f'{self.receipt.receipt_no} - {self.order_item.item.name}'

    def save(self, *args, **kwargs):
        # Adjust received_quantity on order_item
        if self.pk:
            old = GoodsReceiptItem.objects.get(pk=self.pk)
            self.order_item.received_quantity -= old.quantity_received
        super().save(*args, **kwargs)
        self.order_item.received_quantity += self.quantity_received
        self.order_item.save(update_fields=['received_quantity'])
        self.order_item.order.update_status()

    def delete(self, *args, **kwargs):
        order_item = self.order_item
        order_item.received_quantity -= self.quantity_received
        order_item.save(update_fields=['received_quantity'])
        super().delete(*args, **kwargs)
        order_item.order.update_status()
