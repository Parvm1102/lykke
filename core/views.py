from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django import forms
from django.db.models import Min, Q
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay
import json
import uuid
from .models import UserProfile, TravelOption, TravelOptionDetail, TravelOptionImage, Booking, Passenger
from .forms import BookingForm, PassengerFormSet


class UserRegistrationForm(UserCreationForm):
    """Extended registration form with additional fields"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'date_of_birth', 'street_address', 'city', 'pin_code', 'country']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


def home(request):
    """Home page view with featured destinations"""
    # Get featured destinations (limit to 6 for homepage)
    featured_destinations = {}
    
    # Get active travel options
    active_travel_options = TravelOption.objects.filter(
        is_active=True,
        departure_date__gte=timezone.now().date()
    ).select_related('details').prefetch_related('images')[:6]
    
    for option in active_travel_options:
        destination = option.destination
        if destination not in featured_destinations:
            # Get primary image or first image
            primary_image = option.images.filter(is_primary=True).first()
            if not primary_image:
                primary_image = option.images.first()
            
            featured_destinations[destination] = {
                'name': destination,
                'primary_image': primary_image,
                'min_price': option.price_per_seat,
                'travel_types': [option.travel_type],
                'sample_option': option
            }
    
    return render(request, 'core/home.html', {
        'featured_destinations': list(featured_destinations.values())
    })


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'core/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    return render(request, 'core/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'core/edit_profile.html', {'form': form})


def travel_destinations_view(request):
    """View to display all available destinations with primary images"""
    # Get unique destinations with their primary images and minimum prices
    destinations = {}
    
    # Get all active travel options
    active_travel_options = TravelOption.objects.filter(
        is_active=True,
        departure_date__gte=timezone.now().date()
    ).select_related('details').prefetch_related('images')
    
    for option in active_travel_options:
        destination = option.destination
        if destination not in destinations:
            # Get primary image or first image
            primary_image = option.images.filter(is_primary=True).first()
            if not primary_image:
                primary_image = option.images.first()
            
            destinations[destination] = {
                'name': destination,
                'primary_image': primary_image,
                'min_price': option.price_per_seat,
                'travel_types': [option.travel_type],
                'sample_option': option
            }
        else:
            # Update minimum price and add travel type
            if option.price_per_seat < destinations[destination]['min_price']:
                destinations[destination]['min_price'] = option.price_per_seat
            
            if option.travel_type not in destinations[destination]['travel_types']:
                destinations[destination]['travel_types'].append(option.travel_type)
    
    return render(request, 'core/destinations.html', {
        'destinations': destinations.values()
    })


def destination_detail_view(request, destination):
    """Detailed view for a specific destination"""
    # Get all active travel options for this destination
    travel_options = TravelOption.objects.filter(
        destination__iexact=destination,
        is_active=True,
        departure_date__gte=timezone.now().date()
    ).select_related('details').prefetch_related('images').order_by('departure_date', 'departure_time')
    
    if not travel_options.exists():
        messages.error(request, f'No travel options found for {destination}.')
        return redirect('destinations')
    
    # Get destination info from first option
    first_option = travel_options.first()
    destination_images = first_option.images.all().order_by('display_order')
    destination_details = getattr(first_option, 'details', None)
    
    # Group options by travel type
    options_by_type = {}
    for option in travel_options:
        if option.travel_type not in options_by_type:
            options_by_type[option.travel_type] = []
        options_by_type[option.travel_type].append(option)
    
    # Get date filter if provided
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()
            travel_options = travel_options.filter(departure_date=selected_date)
        except ValueError:
            selected_date = None
    
    # Get travel type filter if provided
    selected_type = request.GET.get('type')
    if selected_type:
        travel_options = travel_options.filter(travel_type=selected_type)
    
    return render(request, 'core/destination_detail.html', {
        'destination': destination.title(),
        'travel_options': travel_options,
        'options_by_type': options_by_type,
        'destination_images': destination_images,
        'destination_details': destination_details,
        'selected_date': selected_date,
        'selected_type': selected_type,
    })


@login_required
@login_required
def book_travel_view(request, travel_id):
    """Booking page for a specific travel option"""
    travel_option = get_object_or_404(TravelOption, travel_id=travel_id)
    
    if request.method == 'POST':
        booking_form = BookingForm(request.POST)
        passenger_formset = PassengerFormSet(request.POST)
        
        if booking_form.is_valid() and passenger_formset.is_valid():
            # Create booking
            booking = booking_form.save(commit=False)
            booking.user = request.user
            booking.travel_option = travel_option
            booking.total_price = travel_option.price_per_seat * booking.number_of_seats
            booking.status = 'pending'
            booking.payment_status = 'pending'
            booking.save()
            
            # Create passengers
            for passenger_form in passenger_formset:
                if passenger_form.cleaned_data and not passenger_form.cleaned_data.get('DELETE', False):
                    passenger = passenger_form.save(commit=False)
                    passenger.booking = booking
                    passenger.save()
            
            # Redirect to payment
            return redirect('payment', booking_id=booking.booking_id)
        else:
            # Add error messages for debugging
            for field, errors in booking_form.errors.items():
                for error in errors:
                    messages.error(request, f"Booking {field}: {error}")
            
            for i, form in enumerate(passenger_formset):
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Passenger {i+1} {field}: {error}")
    else:
        booking_form = BookingForm()
        passenger_formset = PassengerFormSet()
    
    return render(request, 'core/booking.html', {
        'travel_option': travel_option,
        'booking_form': booking_form,
        'passenger_formset': passenger_formset,
    })


@login_required
def payment_view(request, booking_id):
    """Payment page using Razorpay"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    # Create Razorpay order
    razorpay_order = client.order.create({
        'amount': int(booking.total_price * 100),  # Amount in paise
        'currency': 'INR',
        'receipt': booking.booking_id,
        'payment_capture': 1
    })
    
    booking.transaction_id = razorpay_order['id']
    booking.save()
    
    context = {
        'booking': booking,
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'user': request.user,
    }
    
    return render(request, 'core/payment.html', context)


@csrf_exempt
@csrf_exempt
def payment_success_view(request):
    """Handle successful payment callback from Razorpay"""
    if request.method == 'POST':
        try:
            # Get payment details from Razorpay
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            booking_id = request.POST.get('booking_id')
            
            print(f"Payment success data: payment_id={payment_id}, order_id={order_id}, booking_id={booking_id}")
            
            if not all([payment_id, order_id, signature, booking_id]):
                messages.error(request, 'Missing payment information. Please try again.')
                return redirect('home')
            
            # Verify payment signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            # Get booking using booking_id - don't require user session for callback
            try:
                booking = Booking.objects.get(booking_id=booking_id)
                # Verify that the order_id matches our transaction_id
                if booking.transaction_id != order_id:
                    print(f"Order ID mismatch: expected {booking.transaction_id}, got {order_id}")
                    messages.error(request, 'Payment order mismatch. Please contact support.')
                    return redirect('home')
            except Booking.DoesNotExist:
                print(f"Booking not found for booking_id: {booking_id}")
                messages.error(request, 'Booking not found. Please contact support.')
                return redirect('home')
            
            # Verify signature
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            
            try:
                client.utility.verify_payment_signature(params_dict)
                
                # Payment successful
                booking.payment_status = 'completed'
                booking.status = 'confirmed'
                booking.payment_method = 'Razorpay'
                booking.payment_date = timezone.now()
                # Store payment ID in a separate field or append to transaction_id
                booking.save()
                
                # Update available seats
                travel_option = booking.travel_option
                travel_option.available_seats -= booking.number_of_seats
                travel_option.save()
                
                messages.success(request, 'Payment successful! Your booking is confirmed.')
                return redirect('booking_confirmation', booking_id=booking.booking_id)
                
            except razorpay.errors.SignatureVerificationError:
                booking.payment_status = 'failed'
                booking.save()
                messages.error(request, 'Payment verification failed. Please try again.')
                return redirect('payment', booking_id=booking.booking_id)
                
        except Exception as e:
            # Log the error for debugging
            print(f"Payment processing error: {str(e)}")
            print(f"POST data: {request.POST}")
            messages.error(request, f'Payment processing error: {str(e)}')
            # Try to redirect to payment page if we have booking_id
            booking_id = request.POST.get('booking_id')
            if booking_id:
                return redirect('payment', booking_id=booking_id)
            return redirect('home')
    
    return redirect('home')


@login_required
def booking_confirmation_view(request, booking_id):
    """Booking confirmation page"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    passengers = booking.passengers.all()
    
    return render(request, 'core/booking_confirmation.html', {
        'booking': booking,
        'passengers': passengers,
    })


@login_required
def my_bookings_view(request):
    """User's booking history"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    
    return render(request, 'core/my_bookings.html', {
        'bookings': bookings,
    })
