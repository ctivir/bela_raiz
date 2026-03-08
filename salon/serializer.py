from rest_framework import serializers
from .models import Booking, SalonService

class SalonServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalonService
        fields = ['id', 'name', 'description', 'price', 'duration_minutes']


class BookingSerializer(serializers.ModelSerializer):
    service = SalonServiceSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'client', 'service', 'scheduled_for', 'status', 'deposit_amount']
        read_only_fields = ['status', 'deposit_amount']
