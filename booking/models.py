from django.conf import settings
from django.db import models


class Booking(models.Model):

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_bookings'
    )

    provider = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='provider_bookings',
    limit_choices_to={'role': 'PROVIDER'}
)

    service = models.CharField(max_length=200)

    booking_date = models.DateField()

    booking_time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.customer.username} - {self.service}"


    class Meta:
      constraints = [
        models.UniqueConstraint(
            fields=[
                "provider",
                "booking_date",
                "booking_time",
            ],
            condition=models.Q(
                status__in=["PENDING", "CONFIRMED"]
            ),
            name="unique_active_provider_booking",
        ),
    ]

