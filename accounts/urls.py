from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import (
    SignupView,
    LoginView,
    profile,
    logout_view,
    add_address,
    set_default_address,
    delete_address,
    update_profile,
)


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('profile/update/', update_profile, name='update_profile'),
    path('address/add/', add_address, name='add_address'),
    path('address/<int:address_id>/set-default/', set_default_address, name='set_default_address'),
    path('address/<int:address_id>/delete/', delete_address, name='delete_address'),
]


