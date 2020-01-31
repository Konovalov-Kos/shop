from django.contrib import admin

from .models import Category, Brand, Product

admin.site.register(Category)
admin.site.register(Brand)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'brand')
    list_filter = ('name', 'brand', 'price')

    fieldsets = (
        ('Имя товара', {
            'fields': ('name',)
        }),
        ('Описание', {
            'fields': ('image', 'description', 'specification', 'brand')
        }),
        ('Цена', {
            'fields': ('price', 'prev_price')
        }),
        ('Категория', {
            'fields': ('category',)
        }),
    )