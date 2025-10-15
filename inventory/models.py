from django.db import models


class StockItem(models.Model):
    variant = models.OneToOneField('catalog.ProductVariant', on_delete=models.CASCADE, related_name='stock')
    quantity_available = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.variant.sku} — {self.quantity_available} available"

# Create your models here.
