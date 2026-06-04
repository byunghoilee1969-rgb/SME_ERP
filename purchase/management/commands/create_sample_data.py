from django.core.management.base import BaseCommand
from django.utils import timezone
from common.models import Supplier, Item
from purchase.models import PurchaseOrder, PurchaseOrderItem, GoodsReceipt, GoodsReceiptItem
import datetime
import decimal


class Command(BaseCommand):
    help = '샘플 데이터를 생성합니다.'

    def handle(self, *args, **options):
        self.stdout.write('샘플 데이터 생성 중...')

        # Suppliers
        suppliers_data = [
            {'code': 'SUP001', 'name': '(주)한국자재', 'business_no': '123-45-67890',
             'contact_person': '김철수', 'phone': '02-1234-5678', 'email': 'kim@hankook.co.kr'},
            {'code': 'SUP002', 'name': '대한부품산업', 'business_no': '234-56-78901',
             'contact_person': '이영희', 'phone': '031-9876-5432', 'email': 'lee@daehan.co.kr'},
            {'code': 'SUP003', 'name': '글로벌소재(주)', 'business_no': '345-67-89012',
             'contact_person': '박민준', 'phone': '051-5555-1234', 'email': 'park@global.co.kr'},
        ]
        suppliers = []
        for data in suppliers_data:
            s, created = Supplier.objects.get_or_create(code=data['code'], defaults=data)
            suppliers.append(s)
            if created:
                self.stdout.write(f'  공급업체 생성: {s.name}')

        # Items
        items_data = [
            {'code': 'ITEM001', 'name': '스테인리스 파이프 (50mm)', 'category': 'RAW',
             'unit': 'M', 'standard_price': decimal.Decimal('15000')},
            {'code': 'ITEM002', 'name': '알루미늄 판재 (2T)', 'category': 'RAW',
             'unit': 'EA', 'standard_price': decimal.Decimal('45000')},
            {'code': 'ITEM003', 'name': '볼트/너트 세트 (M10)', 'category': 'SUB',
             'unit': 'BOX', 'standard_price': decimal.Decimal('8500')},
            {'code': 'ITEM004', 'name': '산업용 윤활유 (20L)', 'category': 'CONSUMABLE',
             'unit': 'CAN', 'standard_price': decimal.Decimal('35000')},
            {'code': 'ITEM005', 'name': '절삭공구 (엔드밀 10mm)', 'category': 'CONSUMABLE',
             'unit': 'EA', 'standard_price': decimal.Decimal('22000')},
            {'code': 'ITEM006', 'name': '고무 패킹 (100mm)', 'category': 'SUB',
             'unit': 'EA', 'standard_price': decimal.Decimal('3200')},
        ]
        items = []
        for data in items_data:
            item, created = Item.objects.get_or_create(code=data['code'], defaults=data)
            items.append(item)
            if created:
                self.stdout.write(f'  품목 생성: {item.name}')

        today = datetime.date.today()

        # Purchase Orders
        if PurchaseOrder.objects.count() == 0:
            # Order 1: COMPLETED
            po1 = PurchaseOrder(
                supplier=suppliers[0],
                order_date=today - datetime.timedelta(days=30),
                expected_date=today - datetime.timedelta(days=20),
                status='COMPLETED',
                notes='정기 발주',
            )
            po1.save()
            oi1 = PurchaseOrderItem.objects.create(order=po1, item=items[0], quantity=50, unit_price=15000)
            oi2 = PurchaseOrderItem.objects.create(order=po1, item=items[2], quantity=10, unit_price=8500)
            po1.update_total_amount()
            self.stdout.write(f'  발주 생성: {po1.order_no} (완료)')

            # Goods Receipt for po1
            gr1 = GoodsReceipt(
                purchase_order=po1,
                receipt_date=today - datetime.timedelta(days=22),
                warehouse='창고 A',
                status='COMPLETED',
            )
            gr1.save()
            # manually set received quantities
            oi1.received_quantity = 50
            oi1.save(update_fields=['received_quantity'])
            oi2.received_quantity = 10
            oi2.save(update_fields=['received_quantity'])
            GoodsReceiptItem.objects.create(receipt=gr1, order_item=oi1, quantity_received=50)
            GoodsReceiptItem.objects.create(receipt=gr1, order_item=oi2, quantity_received=10)
            self.stdout.write(f'  입고 생성: {gr1.receipt_no}')

            # Order 2: CONFIRMED
            po2 = PurchaseOrder(
                supplier=suppliers[1],
                order_date=today - datetime.timedelta(days=10),
                expected_date=today + datetime.timedelta(days=5),
                status='CONFIRMED',
                notes='긴급 발주',
            )
            po2.save()
            PurchaseOrderItem.objects.create(order=po2, item=items[1], quantity=20, unit_price=45000)
            PurchaseOrderItem.objects.create(order=po2, item=items[3], quantity=5, unit_price=35000)
            po2.update_total_amount()
            self.stdout.write(f'  발주 생성: {po2.order_no} (확정)')

            # Order 3: PARTIAL
            po3 = PurchaseOrder(
                supplier=suppliers[2],
                order_date=today - datetime.timedelta(days=5),
                expected_date=today + datetime.timedelta(days=10),
                status='PARTIAL',
            )
            po3.save()
            oi3 = PurchaseOrderItem.objects.create(order=po3, item=items[4], quantity=30, unit_price=22000)
            oi4 = PurchaseOrderItem.objects.create(order=po3, item=items[5], quantity=100, unit_price=3200)
            po3.update_total_amount()
            self.stdout.write(f'  발주 생성: {po3.order_no} (부분입고)')

            gr2 = GoodsReceipt(
                purchase_order=po3,
                receipt_date=today - datetime.timedelta(days=2),
                warehouse='창고 B',
                status='COMPLETED',
            )
            gr2.save()
            oi3.received_quantity = 15
            oi3.save(update_fields=['received_quantity'])
            oi4.received_quantity = 50
            oi4.save(update_fields=['received_quantity'])
            GoodsReceiptItem.objects.create(receipt=gr2, order_item=oi3, quantity_received=15)
            GoodsReceiptItem.objects.create(receipt=gr2, order_item=oi4, quantity_received=50)
            self.stdout.write(f'  입고 생성: {gr2.receipt_no}')

            # Order 4: DRAFT
            po4 = PurchaseOrder(
                supplier=suppliers[0],
                order_date=today,
                expected_date=today + datetime.timedelta(days=14),
                status='DRAFT',
                notes='견적 검토 중',
            )
            po4.save()
            PurchaseOrderItem.objects.create(order=po4, item=items[0], quantity=100, unit_price=14500)
            PurchaseOrderItem.objects.create(order=po4, item=items[1], quantity=50, unit_price=43000)
            po4.update_total_amount()
            self.stdout.write(f'  발주 생성: {po4.order_no} (초안)')

        self.stdout.write(self.style.SUCCESS('샘플 데이터 생성 완료!'))
