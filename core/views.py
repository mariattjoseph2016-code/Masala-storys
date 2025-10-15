from django.shortcuts import render
from catalog.models import Product, Category


def home(request):
    categories = Category.objects.all()[:8]
    featured = Product.objects.filter(is_active=True)[:6]
    return render(request, 'home.html', {"categories": categories, "featured": featured})

def contact(request):
    return render(request, 'contact.html')

# Create your views here.
