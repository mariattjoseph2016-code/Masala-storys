from django.core.management.base import BaseCommand
from catalog.models import Category, Product


PRODUCTS = [
    {
        "name": "Turmeric Powder",
        "slug": "turmeric-powder",
        "category": "Spices",
        "description": "Bright, earthy turmeric powder sourced from the best farms.",
        "mrp": 199,
        "sale_price": 149,
        "stock_quantity": 120,
    },
    {
        "name": "Chilli Powder",
        "slug": "chilli-powder",
        "category": "Spices",
        "description": "Fiery red chilli powder with a bold aroma and balanced heat.",
        "mrp": 179,
        "sale_price": 139,
        "stock_quantity": 80,
    },
    {
        "name": "Coriander Powder",
        "slug": "coriander-powder",
        "category": "Spices",
        "description": "Freshly ground coriander with citrusy, nutty notes.",
        "mrp": 159,
        "sale_price": None,
        "stock_quantity": 100,
    },
    {
        "name": "Garam Masala",
        "slug": "garam-masala",
        "category": "Blends",
        "description": "Aromatic blend of premium spices for rich gravies and curries.",
        "mrp": 249,
        "sale_price": 219,
        "stock_quantity": 60,
    },
    {
        "name": "Cumin Seeds",
        "slug": "cumin-seeds",
        "category": "Whole",
        "description": "Whole cumin seeds with a robust, warm flavor.",
        "mrp": 169,
        "sale_price": None,
        "stock_quantity": 90,
    },
    {
        "name": "Black Pepper",
        "slug": "black-pepper",
        "category": "Whole",
        "description": "Bold and pungent whole black peppercorns.",
        "mrp": 299,
        "sale_price": 259,
        "stock_quantity": 70,
    },
]


class Command(BaseCommand):
    help = "Seed sample categories and products"

    def handle(self, *args, **options):
        cats = {}
        for cat_name in {p["category"] for p in PRODUCTS}:
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={"slug": cat_name.lower()})
            cats[cat_name] = cat

        created = 0
        for data in PRODUCTS:
            product, was_created = Product.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "category": cats[data["category"]],
                    "description": data["description"],
                    "mrp": data["mrp"],
                    "sale_price": data["sale_price"],
                    "stock_quantity": data["stock_quantity"],
                    "is_active": True,
                },
            )
            created += int(was_created)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} products; created {created}, updated {len(PRODUCTS)-created}"))


