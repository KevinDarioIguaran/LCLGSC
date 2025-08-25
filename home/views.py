from django.shortcuts import render
from shop.models import Product, Category, ShowBestOffers


def home_view(request):
    categories_list = Category.objects.all()
    best_offers = ShowBestOffers.objects.filter(active=True)

    category_products = {}

    for category in categories_list:
        products = Product.objects.filter(category=category).order_by('-sales')[:4]
        if products.exists():
            category_products[category] = products

    context = {
        'category_products': category_products,
        'best_offers': best_offers,
    }

    return render(request, 'pages/home/home.html', context)


def about_view(request):
    return render(request, 'pages/home/about.html')
