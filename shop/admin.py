from django.contrib import admin
from .models import Category, Product, ProductReview, Subcategory, Cart, CartItem, ShowBestOffers
from django.utils.translation import gettext_lazy as _   



class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    list_display = ['name', 'category', 'slug']
    prepopulated_fields = {'slug': ('category',)}
    search_fields = ('name', 'category__name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    inlines = [SubcategoryInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'stock', 'available', 'seller', 'category', 'subcategory') 
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__email', 'comment')
    date_hierarchy = 'created_at'



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