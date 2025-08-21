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
from .models import UserProfile, TravelOption, TravelOptionDetail, TravelOptionImage


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
