from django.db import migrations


def add_default_categories(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')

    defaults = [
        ("Whole Spices", "whole-spices"),
        ("Ground Spices & Powders", "ground-spices-powders"),
        ("Spice Blends", "spice-blends"),
        ("Herbs & Leaves", "herbs-leaves"),
        ("Flakes & Crushed", "flakes-crushed"),
    ]

    for name, slug in defaults:
        Category.objects.get_or_create(slug=slug, defaults={"name": name})


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    slugs = [
        "whole-spices",
        "ground-spices-powders",
        "spice-blends",
        "herbs-leaves",
        "flakes-crushed",
    ]
    Category.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0007_rename_spices_to_powdered"),
    ]

    operations = [
        migrations.RunPython(add_default_categories, remove_default_categories),
    ]


