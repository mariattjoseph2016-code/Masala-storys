from django.db import models
from django.utils.text import slugify
from django.templatetags.static import static
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=150, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='children')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    def get_thumbnail_url(self) -> str:
        # Prefer uploaded image; otherwise, map common slugs to local static fallbacks
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        slug = (self.slug or '').lower()
        # Whole spices → whole.jpg
        if slug in ('whole-spices', 'spices', 'whole', 'whole-spice'):
            return static('img/categories/whole.jpg')

        # Ground spices & powders → powder.jpg
        if slug in (
            'ground-spices-powders', 'powders', 'powdered', 'spice-powder', 'masalas', 'masala'
        ):
            return static('img/categories/powder.jpg')

        # Spice blends → blends.jpg
        if slug in ('spice-blends', 'blends', 'blend', 'mixed-spices', 'masala-blends'):
            return static('img/categories/blends.jpg')

        # Herbs & Leaves (if it ever appears) → herbs.svg
        if slug in ('herbs', 'herb', 'herbs-leaves'):
            return static('img/categories/herbs.svg')

        # Flakes & Crushed → flakes.jpg
        if slug in ('flakes-crushed', 'flakes', 'crushed'):
            return static('img/categories/flakes.jpg')
        if slug in ('masalas', 'masala'):
            return static('img/categories/masalas.svg')
        return static('img/categories/default.svg')


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='products/', blank=True, null=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def total_stock(self) -> int:
        return int(self.stock_quantity or 0)

    def get_effective_price(self):
        return self.sale_price if self.sale_price is not None else self.mrp


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=64, unique=True, blank=True)
    unit_size_grams = models.PositiveIntegerField()
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def get_effective_price(self):
        return self.sale_price if self.sale_price is not None else self.mrp

    def __str__(self) -> str:
        return f"{self.product.name} — {self.unit_size_grams}g"

    def save(self, *args, **kwargs):
        if not self.sku:
            base = slugify(self.product.slug or self.product.name)
            base = base[:20]
            candidate = f"{base}-{self.unit_size_grams}g"
            suffix = 1
            Model = self.__class__
            while Model.objects.filter(sku__iexact=candidate).exclude(pk=self.pk).exists():
                suffix += 1
                candidate = f"{base}-{self.unit_size_grams}g-{suffix}"
            self.sku = candidate
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', '-created_at']

    def __str__(self) -> str:
        return f"Image for {self.product.name}"


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self) -> str:
        return f"{self.user.username} - {self.product.name} ({self.rating} stars)"

    def get_star_display(self):
        """Return HTML for star rating display"""
        stars = '★' * self.rating + '☆' * (5 - self.rating)
        return stars
