from django.db.models import Q, Avg
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Review
from .forms import ReviewForm


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    q = request.GET.get('q')
    category_slug = request.GET.get('category')
    sort = request.GET.get('sort', 'name')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    on_sale = request.GET.get('on_sale')

    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if on_sale == '1':
        products = products.filter(sale_price__isnull=False)
    # Annotate effective price for filtering/sorting
    products = products.annotate(eff_price=Coalesce('sale_price', 'mrp'))
    if price_min:
        products = products.filter(eff_price__gte=price_min)
    if price_max:
        products = products.filter(eff_price__lte=price_max)

    # Sorting
    if sort == 'price':
        products = products.order_by('eff_price')
    elif sort == '-price':
        products = products.order_by('-eff_price')
    else:
        products = products.order_by('name')

    categories = Category.objects.all()
    context = {
        'products': products.distinct(),
        'categories': categories,
        'active_category': category_slug,
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'reviews__user'),
        slug=slug,
        is_active=True,
    )
    images = list(product.images.all())
    # Ensure thumbnail appears first if set and not already in images
    if product.thumbnail and not any(img.image.name == product.thumbnail.name for img in images):
        images.insert(0, type('Thumb', (), {'image': product.thumbnail, 'alt_text': product.name})())
    related = Product.objects.filter(is_active=True, category=product.category).exclude(pk=product.pk)[:8]
    
    # Get reviews for this product
    reviews = product.reviews.all()
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = reviews.count()
    
    # Handle review submission
    if request.method == 'POST' and 'submit_review' in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to submit a review.')
            return redirect('accounts:login')
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            if existing_review:
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.text = form.cleaned_data['text']
                existing_review.save()
                messages.success(request, 'Your review has been updated successfully!')
            else:
                # Create new review
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Thank you for your review!')
            
            return redirect('catalog:product_detail', slug=product.slug)
    else:
        form = ReviewForm()
    
    # Get user's existing review if any
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
    
    context = {
        'product': product, 
        'images': images, 
        'related': related,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'form': form,
        'user_review': user_review,
    }
    return render(request, 'catalog/product_detail.html', context)

# Create your views here.
