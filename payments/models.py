from django.db import models
from django.conf import settings


class Payment(models.Model):
    PAYMENT_TYPES = [
        ('booking_deposit', 'Booking Deposit'),
        ('booking_full', 'Full Booking Payment'),
        ('reseller_order', 'Reseller Order Payment'),
        ('delivery_fee', 'Delivery Fee'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    # Related objects
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

    # Payment details
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='MZN')  # Mozambican Metical

    # M-Pesa specific fields
    mpesa_reference = models.CharField(max_length=100, unique=True)
    mpesa_transaction_id = models.CharField(max_length=100, null=True, blank=True)
    mpesa_receipt_number = models.CharField(max_length=100, null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Phone number used for payment
    phone_number = models.CharField(max_length=15)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.payment_type} - {self.amount} {self.currency} - {self.status}"

    @property
    def is_successful(self):
        return self.status == 'completed'

    @property
    def can_refund(self):
        return self.status == 'completed' and not hasattr(self, 'refund')

    def mark_completed(self, transaction_id=None, receipt_number=None):
        """Mark payment as completed"""
        from django.utils import timezone

        self.status = 'completed'
        self.completed_at = timezone.now()
        if transaction_id:
            self.mpesa_transaction_id = transaction_id
        if receipt_number:
            self.mpesa_receipt_number = receipt_number
        self.save()

        # Update related booking/order status
        self._update_related_status()

    def _update_related_status(self):
        """Update the status of related booking or order"""
        if self.booking and self.payment_type == 'booking_deposit':
            self.booking.status = 'deposit_paid'
            self.booking.save()
        elif self.booking and self.payment_type == 'booking_full':
            self.booking.status = 'confirmed'
            self.booking.save()


class Refund(models.Model):
    original_payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name='refund'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    mpesa_reference = models.CharField(max_length=100, unique=True, null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=Payment.STATUS_CHOICES,
        default='pending'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund for {self.original_payment} - {self.amount}"
