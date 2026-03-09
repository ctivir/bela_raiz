from django.db import models
from django.conf import settings


class Delivery(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Assignment'),
        ('assigned', 'Assigned to Courier'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Delivery Failed'),
        ('cancelled', 'Cancelled'),
    ]

    # Related objects (can be salon booking, reseller order, etc.)
    booking = models.OneToOneField(
        'salon.Booking',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    reseller_order = models.OneToOneField(
        'reseller.Order',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Courier assignment
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'courier'},
        related_name='deliveries'
    )

    # Delivery details
    pickup_address = models.TextField()
    delivery_address = models.TextField()

    # Geolocation
    pickup_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    pickup_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    delivery_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    delivery_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    actual_delivery_time = models.DateTimeField(null=True, blank=True)

    # Additional info
    special_instructions = models.TextField(blank=True)
    tracking_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.booking:
            return f"Delivery for Booking {self.booking.id}"
        elif self.reseller_order:
            return f"Delivery for Order {self.reseller_order.id}"
        return f"Delivery {self.id}"

    @property
    def delivery_type(self):
        if self.booking:
            return 'salon_service'
        elif self.reseller_order:
            return 'reseller_order'
        return 'unknown'

    def assign_courier(self, courier):
        """Assign a courier to this delivery"""
        self.courier = courier
        self.status = 'assigned'
        self.save()

    def update_status(self, new_status, notes=None):
        """Update delivery status with optional notes"""
        self.status = new_status
        if new_status == 'delivered':
            from django.utils import timezone
            self.actual_delivery_time = timezone.now()
        self.save()

        # Create status update record
        DeliveryStatusUpdate.objects.create(
            delivery=self,
            status=new_status,
            notes=notes
        )


class DeliveryStatusUpdate(models.Model):
    delivery = models.ForeignKey(
        Delivery,
        on_delete=models.CASCADE,
        related_name='status_updates'
    )
    status = models.CharField(max_length=20, choices=Delivery.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.delivery} - {self.status} at {self.created_at}"
