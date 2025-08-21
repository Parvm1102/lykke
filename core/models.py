from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid


class UserProfile(models.Model):
    """Extended user profile with detailed address information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Detailed Address Fields
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class TravelOption(models.Model):
    """Model for travel options like flights, trains, and buses"""
    TRAVEL_TYPES = [
        ('flight', 'Flight'),
        ('train', 'Train'),
        ('bus', 'Bus'),
    ]
    
    travel_id = models.CharField(max_length=20, unique=True, editable=False)
    travel_type = models.CharField(max_length=10, choices=TRAVEL_TYPES)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_date = models.DateField()
    arrival_time = models.TimeField()
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    operator_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.travel_id:
            # Generate unique travel ID
            prefix = self.travel_type.upper()[:2] if self.travel_type else 'TR'
            self.travel_id = f"{prefix}{str(uuid.uuid4().int)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.travel_id} - {self.source} to {self.destination}"

    class Meta:
        verbose_name = "Travel Option"
        verbose_name_plural = "Travel Options"
        ordering = ['departure_date', 'departure_time']


class TravelOptionDetail(models.Model):
    """Model for storing travel option images and description"""
    travel_option = models.OneToOneField(TravelOption, on_delete=models.CASCADE, related_name='details')
    description = models.TextField(blank=True, help_text="Detailed description of the travel option")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Details for {self.travel_option.travel_id}"

    class Meta:
        verbose_name = "Travel Option Detail"
        verbose_name_plural = "Travel Option Details"


class TravelOptionImage(models.Model):
    """Model for storing multiple images for travel options"""
    travel_option = models.ForeignKey(TravelOption, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500, help_text="Cloudinary image URL")
    image_title = models.CharField(max_length=100, blank=True, help_text="Optional title for the image")
    is_primary = models.BooleanField(default=False, help_text="Mark as primary image for display")
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which images should be displayed")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Check if this is a new instance
        is_new = self.pk is None
        
        # If this is the first image for this travel option, make it primary
        if is_new and not self.is_primary:
            existing_images = TravelOptionImage.objects.filter(travel_option=self.travel_option).exists()
            if not existing_images:
                self.is_primary = True
        
        # Save the instance first
        super().save(*args, **kwargs)
        
        # If this image is set as primary, update other images after saving
        if self.is_primary:
            TravelOptionImage.objects.filter(
                travel_option=self.travel_option,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

    def __str__(self):
        return f"Image for {self.travel_option.travel_id} - {self.image_title or 'Untitled'}"

    class Meta:
        verbose_name = "Travel Option Image"
        verbose_name_plural = "Travel Option Images"
        ordering = ['display_order', 'created_at']


class Booking(models.Model):
    """Model for user bookings with billing information"""
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    travel_option = models.ForeignKey(TravelOption, on_delete=models.CASCADE, related_name='bookings')
    number_of_seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=BOOKING_STATUS, default='pending')
    
    # Billing Information (non-sensitive)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)  # e.g., 'Credit Card', 'PayPal', 'Bank Transfer'
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    # Billing Address
    billing_name = models.CharField(max_length=100, blank=True)
    billing_street_address = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_pin_code = models.CharField(max_length=10, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            # Generate unique booking ID
            self.booking_id = f"BK{str(uuid.uuid4().int)[:10]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_id} - {self.user.username}"

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-booking_date']


class Passenger(models.Model):
    """Model for individual passenger details"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    seat_number = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.booking.booking_id}"

    class Meta:
        verbose_name = "Passenger"
        verbose_name_plural = "Passengers"
