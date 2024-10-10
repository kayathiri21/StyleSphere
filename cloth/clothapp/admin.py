from django.contrib import admin
from .models import MainCategory, SubCategory, Product,Cart,CartItem,Order,OrderItem
from django.utils.text import slugify
# Register your models here.
@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    list_filter = []  # You can add filters if needed
    exclude = ('slug',)  # Exclude the slug field from the form

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_category', 'slug')
    search_fields = ('name',)
    list_filter = ['main_category']  # You can filter by main category
    exclude = ('slug',)  # Exclude the slug field from the form

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_in_stock', 'brand', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'brand')
    list_filter = ['is_active', 'brand', 'available_colors', 'available_sizes']  # Filter by active status, brand, colors, and sizes
    exclude = ('slug',)  # Exclude the slug field from the form

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = slugify(obj.name)
        super().save_model(request, obj, form, change)

    def get_discounted_price(self, obj):
        return obj.get_discounted_price()
    get_discounted_price.short_description = 'Discounted Price'

admin.site.register(Cart)
admin.site.register(CartItem)

admin.site.register(Order)
admin.site.register(OrderItem)


















# @admin.register: This decorator directly registers the model with its admin class. It's a more concise way to handle model registration in Django.
# admin.site.register: This method manually registers the model and the corresponding admin class. You pass the model (MainCategory) and the admin class (MainCategoryAdmin) as arguments to this function.