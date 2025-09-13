from django.shortcuts import render
from shop.models import Product, Category, ShowBestOffers


def home_view(request):
    categories_list = Category.objects.all()
    best_offers = ShowBestOffers.objects.filter(active=True)

    category_products = {}

    for category in categories_list:
        products = Product.objects.filter(category=category).order_by("-offer_active", "-sales")[:4]
        if products.exists():
            category_products[category] = products

    context = {
        'category_products': category_products,
        'best_offers': best_offers,  
    }

    return render(request, 'pages/home/home.html', context)

def offers_view(request):
    all_offers = Product.objects.filter(offer_active=True).order_by('-discount_percent', '-sales')

    category_dict = {}
    for product in all_offers:
        category_name = product.category.name
        category_dict.setdefault(category_name, []).append(product)

    context = {
        'search_results': all_offers, 
        'categories': category_dict,
        'search_query': 'Ofertas',
        'results_empty': 'No se hay ofertas aún.',
    }

    return render(request, 'pages/shop/search/search.html', context)

def best_sellers_view(request):
    best_sellers = Product.objects.all().order_by('-sales')[:22]

    category_dict = {}

    for product in best_sellers:
        category_name = product.category.name
        category_dict.setdefault(category_name, []).append(product) 
        
    context = {
        'search_results': best_sellers,
        'categories': category_dict,
        'search_query': 'Lo más Vendido',
        'results_empty': 'No se han vendido productos aún.',
    }
    return render(request, 'pages/shop/search/search.html', context)

def customer_service_view(request):
    return render(request, 'pages/home/customer_service.html')

def about_view(request):
    return render(request, 'pages/home/about.html')
