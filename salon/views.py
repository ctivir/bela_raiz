from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import SalonService, Booking
from .serializers import BookingSerializer

@api_view(['POST'])
def create_booking(request):
    service_id = request.data.get('service_id')
    scheduled_for = request.data.get('scheduled_for')
    client = request.user

    try:
        service = SalonService.objects.get(id=service_id)
    except SalonService.DoesNotExist:
        return Response({"error": "Service not found"}, status=status.HTTP_404_NOT_FOUND)

    # Business rule: 20% deposit if price > 1000 MT
    deposit = 0
    if service.price > 1000:
        deposit = service.price * 0.20

    booking = Booking.objects.create(
        client=client,
        service=service,
        scheduled_for=scheduled_for,
        deposit_amount=deposit,
        status='pending'
    )

    serializer = BookingSerializer(booking)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
