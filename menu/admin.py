from unicodedata import category
from django.contrib import admin
from menu.models import Category, FoodItem

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':['category_name']}
    list_display  = ['category_name', 'vendor', 'updated_at']
    search_fields = ['category_name', 'vendor__vendor_name']
admin.site.register(Category, CategoryAdmin)


class FoodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ['food_title']}
    list_display = ['food_title','category', 'vendor', 'price', 'is_available', 'updated_at']
    search_fields = ['food_title', 'vendor__vendor_name', 'category__category_name', 'price']
    list_filter = ['is_available']
admin.site.register(FoodItem, FoodItemAdmin)