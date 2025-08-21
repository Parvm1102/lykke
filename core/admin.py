from django.contrib import admin
from .models import UserProfile, TravelOption, TravelOptionDetail, TravelOptionImage, Booking, Passenger


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'city', 'country', 'created_at']
    list_filter = ['country', 'city', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number', 'city']
    readonly_fields = ['created_at', 'updated_at']


class TravelOptionImageInline(admin.TabularInline):
    model = TravelOptionImage
    extra = 1
    fields = ['image_url', 'image_title', 'is_primary', 'display_order']
    readonly_fields = ['created_at']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Add help text for primary image
        formset.form.base_fields['is_primary'].help_text = (
            "Only one image can be primary per travel option. "
            "Setting this will automatically unset other primary images."
        )
        return formset


class TravelOptionDetailInline(admin.StackedInline):
    model = TravelOptionDetail
    extra = 0
    fields = ['description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TravelOption)
class TravelOptionAdmin(admin.ModelAdmin):
    list_display = ['travel_id', 'travel_type', 'source', 'destination', 'departure_date', 'price_per_seat', 'available_seats', 'is_active']
    list_filter = ['travel_type', 'is_active', 'departure_date', 'source', 'destination']
    search_fields = ['travel_id', 'source', 'destination', 'operator_name']
    readonly_fields = ['travel_id', 'created_at', 'updated_at']
    list_editable = ['is_active']
    date_hierarchy = 'departure_date'
    inlines = [TravelOptionDetailInline, TravelOptionImageInline]


@admin.register(TravelOptionDetail)
class TravelOptionDetailAdmin(admin.ModelAdmin):
    list_display = ['travel_option', 'created_at']
    search_fields = ['travel_option__travel_id', 'travel_option__source', 'travel_option__destination']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TravelOptionImage)
class TravelOptionImageAdmin(admin.ModelAdmin):
    list_display = ['travel_option', 'image_title', 'is_primary', 'display_order', 'created_at']
    list_filter = ['is_primary', 'created_at', 'travel_option__travel_type']
    search_fields = ['travel_option__travel_id', 'image_title', 'travel_option__destination']
    readonly_fields = ['created_at']
    list_editable = ['display_order']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Add help text for primary image
        if 'is_primary' in form.base_fields:
            form.base_fields['is_primary'].help_text = (
                "Only one image can be primary per travel option. "
                "Setting this will automatically unset other primary images for this travel option."
            )
        return form


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'user', 'travel_option', 'number_of_seats', 'total_price', 'status', 'payment_status', 'booking_date']
    list_filter = ['status', 'payment_status', 'booking_date', 'travel_option__travel_type']
    search_fields = ['booking_id', 'user__username', 'user__email', 'transaction_id']
    readonly_fields = ['booking_id', 'created_at', 'updated_at']
    list_editable = ['status', 'payment_status']
    date_hierarchy = 'booking_date'


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'age', 'gender', 'booking', 'seat_number']
    list_filter = ['gender', 'booking__travel_option__travel_type']
    search_fields = ['first_name', 'last_name', 'booking__booking_id']
    readonly_fields = ['created_at']
