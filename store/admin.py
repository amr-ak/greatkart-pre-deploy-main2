from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import Product, ProductVariant, ProductGallery, ReviewRating, VariationCategory, VariationOption, UserActivityLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_available', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='product-analytics'),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            title='Analytics Dashboard',
        )
        return TemplateResponse(request, "admin/analytics.html", context)

# تسجيل باقي الموديلات
admin.site.register(ProductVariant)
admin.site.register(ProductGallery)
admin.site.register(ReviewRating)
admin.site.register(VariationCategory)
admin.site.register(VariationOption)
admin.site.register(UserActivityLog)
