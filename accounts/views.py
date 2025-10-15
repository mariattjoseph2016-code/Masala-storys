from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomUserCreationForm
from .models import Address

User = get_user_model()


class SignupView(View):
    def get(self, request):
        return render(request, 'accounts/signup.html', {'form': CustomUserCreationForm()})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('accounts:profile')
        return render(request, 'accounts/signup.html', {'form': form})


class LoginView(View):
    def get(self, request):
        return render(request, 'accounts/login.html', {'form': AuthenticationForm()})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('accounts:profile')
        return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


def logout_view(request):
    """Custom logout view that handles both GET and POST requests"""
    if request.user.is_authenticated:
        auth_logout(request)
        messages.success(request, 'You have been successfully logged out.')
    return redirect('home')  # Redirect to home page instead of login page


@login_required
def add_address(request):
    """Add a new address for the user"""
    if request.method == 'POST':
        # Create new address
        address = Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            line1=request.POST.get('line1'),
            line2=request.POST.get('line2', ''),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country', 'IN'),
            is_default=request.POST.get('is_default') == 'on'
        )
        
        # If this is set as default, unset others
        if address.is_default:
            Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
        
        messages.success(request, 'Address added successfully!')
        return redirect('accounts:profile')
    
    return redirect('accounts:profile')


@login_required
@require_POST
def set_default_address(request, address_id):
    """Set an address as default"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Unset all other default addresses
    Address.objects.filter(user=request.user).update(is_default=False)
    
    # Set this address as default
    address.is_default = True
    address.save()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def delete_address(request, address_id):
    """Delete an address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    
    return JsonResponse({'success': True})


@login_required
def update_profile(request):
    """Update user profile information"""
    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return redirect('accounts:profile')
