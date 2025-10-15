from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "city", "state", "postal_code", "is_default")
    list_filter = ("is_default", "state", "country")
    search_fields = ("full_name", "city", "postal_code", "user__username", "user__email")

# Register your models here.
