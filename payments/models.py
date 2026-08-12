from django.db import models

from django.db import models
from booking.models import Booking


class Payment(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"