from catalog.models import Category


def nav_categories(request):
    try:
        cats = Category.objects.all().order_by('name')[:10]
    except Exception:
        cats = []
    return {"categories": cats}


