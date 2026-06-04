from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.PurchaseOrderListView.as_view(), name='order_list'),
    path('orders/new/', views.PurchaseOrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='order_detail'),
    path('orders/<int:pk>/edit/', views.PurchaseOrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/confirm/', views.PurchaseOrderConfirmView.as_view(), name='order_confirm'),
    path('receipts/', views.GoodsReceiptListView.as_view(), name='receipt_list'),
    path('receipts/new/', views.GoodsReceiptCreateView.as_view(), name='receipt_create'),
    path('receipts/<int:pk>/', views.GoodsReceiptDetailView.as_view(), name='receipt_detail'),
    path('ajax/order-items/', views.get_order_items_ajax, name='ajax_order_items'),
]
