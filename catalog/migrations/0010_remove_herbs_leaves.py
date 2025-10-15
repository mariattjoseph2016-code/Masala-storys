from django.db import migrations


def remove_herbs_leaves(apps, schema_editor):
    Category = apps.get_model('catalog', 'Category')
    Product = apps.get_model('catalog', 'Product')

    target = Category.objects.filter(slug='herbs-leaves').first()
    if not target:
        return

    # Reassign products to Whole Spices (fallback to first available)
    fallback = Category.objects.filter(slug='whole-spices').first() or Category.objects.exclude(pk=target.pk).first()
    if fallback:
        Product.objects.filter(category=target).update(category=fallback)

    target.delete()


def noop(apps, schema_editor):
    # irreversible
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_prune_categories'),
    ]

    operations = [
        migrations.RunPython(remove_herbs_leaves, noop),
    ]


