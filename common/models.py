from django.db import models


class Supplier(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='공급업체코드')
    name = models.CharField(max_length=100, verbose_name='공급업체명')
    business_no = models.CharField(max_length=20, blank=True, verbose_name='사업자번호')
    contact_person = models.CharField(max_length=50, blank=True, verbose_name='담당자')
    phone = models.CharField(max_length=20, blank=True, verbose_name='전화번호')
    email = models.EmailField(blank=True, verbose_name='이메일')
    address = models.TextField(blank=True, verbose_name='주소')
    is_active = models.BooleanField(default=True, verbose_name='사용여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')

    class Meta:
        verbose_name = '공급업체'
        verbose_name_plural = '공급업체 목록'
        ordering = ['name']

    def __str__(self):
        return f"[{self.code}] {self.name}"


class Item(models.Model):
    CATEGORY_CHOICES = [
        ('RAW', '원자재'),
        ('SUB', '부자재'),
        ('CONSUMABLE', '소모품'),
        ('EQUIPMENT', '설비'),
        ('OTHER', '기타'),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name='품목코드')
    name = models.CharField(max_length=100, verbose_name='품목명')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='RAW', verbose_name='분류')
    unit = models.CharField(max_length=20, default='EA', verbose_name='단위')
    standard_price = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name='표준단가')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='사용여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')

    class Meta:
        verbose_name = '품목'
        verbose_name_plural = '품목 목록'
        ordering = ['name']

    def __str__(self):
        return f"[{self.code}] {self.name}"
