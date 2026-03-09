from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import SalonService, Booking
from .serializer import (
    BookingSerializer, BookingCreateSerializer,
    SalonServiceSerializer
)


class BookingViewSet(ModelViewSet):
    """
    ViewSet for managing bookings with full CRUD operations.
    """
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'service', 'client']
    ordering_fields = ['scheduled_for', 'created_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        """
        Filter bookings based on user role:
        - Clients see only their bookings
        - Salon owners see bookings for their services
        """
        user = self.request.user
        if hasattr(user, 'role'):
            if user.role == 'client':
                return Booking.objects.filter(client=user)
            elif user.role == 'salon':
                return Booking.objects.filter(service__salon=user)
        return Booking.objects.none()

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking (only by client or salon owner)"""
        booking = self.get_object()
        user = request.user

        # Check permissions
        if user.role == 'client' and booking.client != user:
            return Response(
                {"error": "You can only cancel your own bookings."},
                status=status.HTTP_403_FORBIDDEN
            )
        if user.role == 'salon' and booking.service.salon != user:
            return Response(
                {"error": "You can only cancel bookings for your services."},
                status=status.HTTP_403_FORBIDDEN
            )

        if booking.status in ['completed', 'cancelled']:
            return Response(
                {"error": "Cannot cancel a completed or already cancelled booking."},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.save()

        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class SalonServiceListView(generics.ListAPIView):
    """
    List all active salon services.
    """
    queryset = SalonService.objects.filter(is_active=True)
    serializer_class = SalonServiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['salon']
    ordering_fields = ['name', 'price']
    ordering = ['name']
