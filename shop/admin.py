from django.contrib import admin
from .models import Category, Product, Cart, CartItem, ShowBestOffers
from django.utils.translation import gettext_lazy as _   



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'stock', 'available', 'seller', 'category') 
    prepopulated_fields = {'slug': ('name',)}


class CartItemInline(admin.TabularInline):
    list_display = ('cart', 'product_id', 'quantity',)
    model = CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',  'created_at')
    inlines = [CartItemInline]


@admin.register(ShowBestOffers)
class ShowBestOffersAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('category__name',)