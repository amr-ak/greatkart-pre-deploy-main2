from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/<str:order_number>/', views.order_complete, name='order_complete'),
    path('merchant-orders/', views.merchant_orders, name='merchant_orders'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
