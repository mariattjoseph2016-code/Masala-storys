from django.db import migrations


ALLOWED_SLUGS = {
    "whole-spices",
    "ground-spices-powders",
    "spice-blends",
    "herbs-leaves",
    "flakes-crushed",
}


def reassign_and_delete(apps, schema_editor):
    Category = apps.get_model("catalog", "Category")
    Product = apps.get_model("catalog", "Product")

    # Pick a default category to reassign to (Spice Blends)
    default_cat = Category.objects.filter(slug="spice-blends").first()
    if default_cat is None:
        # Fallback to any allowed category
        default_cat = Category.objects.filter(slug__in=ALLOWED_SLUGS).first()

    # Reassign products that belong to disallowed categories
    disallowed = Category.objects.exclude(slug__in=ALLOWED_SLUGS)
    if default_cat is not None:
        Product.objects.filter(category__in=disallowed).update(category=default_cat)

    # Delete disallowed categories (now unused after reassignment)
    disallowed.delete()


def noop_reverse(apps, schema_editor):
    # Irreversible cleanup
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_default_categories"),
    ]

    operations = [
        migrations.RunPython(reassign_and_delete, noop_reverse),
    ]


