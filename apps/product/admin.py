from django.contrib import admin
from .models import Category, Product, ProductViews, Image, Color, Size

admin.site.register(Category)
admin.site.register(ProductViews)
admin.site.register(Color)
admin.site.register(Size)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'quantity', 'views', 'is_active',)
    search_fields = ('title', 'category__name')
    list_filter = ('category', 'is_active')


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
