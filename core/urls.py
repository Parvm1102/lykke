from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('destinations/', views.travel_destinations_view, name='destinations'),
    path('destination/<str:destination>/', views.destination_detail_view, name='destination_detail'),
    path('book/<str:travel_id>/', views.book_travel_view, name='book_travel'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
    path('payment/<str:booking_id>/', views.payment_view, name='payment'),
    path('booking/confirmation/<str:booking_id>/', views.booking_confirmation_view, name='booking_confirmation'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
]
