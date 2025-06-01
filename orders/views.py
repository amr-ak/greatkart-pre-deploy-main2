from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from carts.models import CartItem
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import datetime
import uuid



@csrf_exempt
def payments(request):
    if request.method == 'POST':
        order_id = request.POST.get('orderID')
        trans_id = str(uuid.uuid4())
        payment_method = request.POST.get('payment_method')
        status = 'Completed'
        amount_paid = float(request.POST.get('amount_paid'))

        try:
            payment = Payment(
                user=request.user,
                payment_id=trans_id,
                payment_method=payment_method,
                amount_paid=amount_paid,
                status=status,
            )
            payment.save()

            # جلب الطلب
            order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_id)

            # تحقق من تطابق المبلغ المدفوع مع المبلغ الإجمالي للطلب
            if amount_paid != order.order_total:
                messages.error(request, "المبلغ المدفوع لا يتطابق مع المبلغ الإجمالي للطلب.")
                return redirect('store')

            order.payment = payment
            order.is_ordered = True
            order.save()

            cart_items = CartItem.objects.filter(user=request.user)
            for item in cart_items:
                order_product = OrderProduct()
                order_product.order = order
                order_product.payment = payment
                order_product.user = request.user
                order_product.product = item.product
                order_product.quantity = item.quantity
                order_product.product_price = item.product.price
                order_product.ordered = True
                order_product.save()

                if item.variations.exists():
                    order_product.variations.set(item.variations.all())

            cart_items.delete()

            return render(request, 'orders/payments.html', {'order_number': order.order_number})
        except Order.DoesNotExist:
            messages.error(request, "الطلب غير موجود.")
            return redirect('store')
    else:
        return redirect('store')


@login_required
def payment_methods(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if order.is_ordered:
        messages.error(request, "تم الدفع لهذا الطلب بالفعل.")
        return redirect('order_complete', order_number=order_number)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method:
            order.payment_method = payment_method
            order.is_ordered = True  # تغيير الحالة إلى "تم الدفع"
            order.save()

            current_user = request.user
            current_user.has_paid = True  # تحديث حالة الدفع في الملف الشخصي للمستخدم
            current_user.save()

            return redirect('order_complete', order_number=order_number)

    context = {
        'order': order,
    }

    return render(request, 'orders/payments.html', context)


@login_required
def place_order(request, total=0, quantity=0):
    if request.method == "POST":
        current_user = request.user
        cart_items = CartItem.objects.filter(user=current_user)
        if not cart_items.exists():
            messages.error(request, "سلة التسوق فارغة!")
            return redirect('store')

        for item in cart_items:
            total += (item.product.price * item.quantity)
            quantity += item.quantity

        order = Order.objects.create(
            user=current_user,
            order_total=total,
            is_ordered=False,
            status="Pending"
        )

        for item in cart_items:
            OrderProduct.objects.create(
                order=order,
                product=item.product,
                user=current_user,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=False
            )

        cart_items.delete()

        messages.success(request, "تم تسجيل الطلب بنجاح!")
        return redirect('order_complete', order_number=order.order_number)

    return redirect('store')

@login_required
def order_complete(request, order_number):
    try:
        order = get_object_or_404(Order, order_number=order_number, is_ordered=True)
    except:
        return render(request, 'orders/order_complete.html', {'message': 'الطلب غير موجود أو لم يكتمل'})

    payment = order.payment if order.payment else None
    ordered_products = OrderProduct.objects.filter(order=order)

    subtotal = sum(item.product_price * item.quantity for item in ordered_products)

    context = {
        'order': order,
        'ordered_products': ordered_products,
        'order_number': order.order_number,
        'transID': payment.payment_id if payment else None,
        'payment': payment,
        'subtotal': subtotal
    }
    return render(request, 'orders/order_complete.html', context)



@staff_member_required
def merchant_orders(request):
    status_filter = request.GET.get('status', None)
    orders = Order.objects.all().order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'orders/merchant_orders.html', {'orders': orders})

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["Pending", "Completed", "Cancelled"]:
            order.status = new_status
            order.save()
            messages.success(request, "تم تحديث حالة الطلب بنجاح!")
        return redirect('merchant_orders')
    return JsonResponse({'message': 'Invalid request'}, status=400)
