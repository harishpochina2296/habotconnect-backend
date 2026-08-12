from rest_framework import serializers
from .models import Booking
from django.utils import timezone

class BookingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking

        fields = [
            'id',
            'customer',
            'provider',
            'service',
            'booking_date',
            'booking_time',
            'status',
            'notes',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'customer',
            'provider',
            'status',
            'created_at',
            'updated_at',
        ]

    def validate_booking_date(self, value):

        today = timezone.localdate()

        if value < today:
            raise serializers.ValidationError(
                "Booking date cannot be in the past."
            )

        return value