from rest_framework import serializers
from django.utils import timezone
from .models import Booking, SalonService

class SalonServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalonService
        fields = ['id', 'name', 'description', 'price', 'duration_minutes']


class BookingSerializer(serializers.ModelSerializer):
    service = SalonServiceSerializer(read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    salon_name = serializers.CharField(source='service.salon.get_full_name', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'client', 'client_name', 'service', 'salon_name',
            'scheduled_for', 'status', 'deposit_amount', 'mpesa_reference',
            'created_at'
        ]
        read_only_fields = ['id', 'client', 'status', 'deposit_amount', 'client_name', 'salon_name', 'created_at']

    def validate_scheduled_for(self, value):
        """Validate that booking is not in the past"""
        if value <= timezone.now():
            raise serializers.ValidationError("Cannot book appointments in the past.")
        return value

    def validate_service_id(self, value):
        """Validate that service exists and belongs to a salon"""
        try:
            service = SalonService.objects.get(id=value, is_active=True)
            return service
        except SalonService.DoesNotExist:
            raise serializers.ValidationError("Service not found or inactive.")


class BookingCreateSerializer(serializers.ModelSerializer):
    service_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = ['service_id', 'scheduled_for']

    def validate_service_id(self, value):
        try:
            service = SalonService.objects.get(id=value, is_active=True)
            return service
        except SalonService.DoesNotExist:
            raise serializers.ValidationError("Service not found or inactive.")

    def create(self, validated_data):
        service = validated_data.pop('service_id')
        client = self.context['request'].user

        # Business rule: 20% deposit if price > 1000 MT
        deposit = 0
        if service.price > 1000:
            deposit = service.price * 0.20

        booking = Booking.objects.create(
            client=client,
            service=service,
            deposit_amount=deposit,
            **validated_data
        )
        return booking
