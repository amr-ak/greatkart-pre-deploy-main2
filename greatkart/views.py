from django.shortcuts import render # type: ignore
from store.models import Product, ReviewRating
from . import views


def home(request):
    products = Product.objects.filter(is_available=True).order_by('created_at')

    # Get the reviews
    reviews = None
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        'products': products,
        'reviews': reviews,
    }
    return render(request, 'home.html', context)


def support_ticket(request):
    return render(request, 'support_ticket.html')

def contact(request):
    return render(request, 'contact.html')

def help(request):
    return render(request, 'help.html')