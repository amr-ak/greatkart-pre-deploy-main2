from django.db import models # type: ignore
from django.utils.text import slugify # type: ignore
from django.urls import reverse # type: ignore
from accounts.models import Account  # تأكد من استيراد الحساب



# ========================
# Product Model
# ========================

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', default='default/DragoKart logo.png') 
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_url(self):
        return reverse('product_detail', args=[self.slug])

    def __str__(self):
        return self.name


# ========================
# Variation Management (Categories + Options)
# ========================

class VariationCategory(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class VariationOption(models.Model):
    category = models.ForeignKey(VariationCategory, on_delete=models.CASCADE, related_name='options')
    value = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.category.name}: {self.value}"

# ========================
# Product Variant (Combining color, size, volume)
# ========================

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.ForeignKey(
        VariationOption,
        on_delete=models.CASCADE,
        related_name='color_variants',
        limit_choices_to={'category__name': 'Color'}
    )
    size = models.ForeignKey(
        VariationOption,
        on_delete=models.CASCADE,
        related_name='size_variants',
        limit_choices_to={'category__name': 'Size'}
    )
    volume = models.ForeignKey(
        VariationOption,
        on_delete=models.CASCADE,
        related_name='volume_variants',
        limit_choices_to={'category__name': 'Volume'}
    )
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.color.value} / {self.size.value} / {self.volume.value}"

    def is_in_stock(self):
        return self.stock > 0


# ========================
# Product Gallery
# ========================

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'


# ========================
# Review & Rating
# ========================

class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class UserActivityLog(models.Model):
    ACTIVITY_CHOICES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('add_to_cart', 'Add to Cart'),
        ('purchase', 'Purchase'),
    ]
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.product.product_name}"