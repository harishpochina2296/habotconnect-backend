from datetime import date, time

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from booking.models import Booking

from .models import Payment
from .serializers import PaymentWebhookSerializer


User = get_user_model()

class PaymentWebhookSerializerTestCase(APITestCase):

    def test_valid_success_payload(self):

        data = {
            "event": "payment.success",
            "booking_id": 1,
            "transaction_id": "txn_10001",
            "amount": "500.00",
        }

        serializer = PaymentWebhookSerializer(
            data=data
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors
        )

    def test_valid_failed_payload(self):

        data = {
            "event": "payment.failed",
            "booking_id": 1,
            "transaction_id": "txn_10002",
            "amount": "500.00",
        }

        serializer = PaymentWebhookSerializer(
            data=data
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors
        )

    def test_invalid_event(self):

        data = {
            "event": "random.event",
            "booking_id": 1,
            "transaction_id": "txn_10003",
            "amount": "500.00",
        }

        serializer = PaymentWebhookSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )

    def test_invalid_booking_id(self):

        data = {
            "event": "payment.success",
            "booking_id": 0,
            "transaction_id": "txn_10004",
            "amount": "500.00",
        }

        serializer = PaymentWebhookSerializer(
            data=data
        )

        self.assertFalse(
            serializer.is_valid()
        )
class PaymentWebhookTestCase(APITestCase):

    def setUp(self):

        self.customer = User.objects.create_user(
            username="payment_customer",
            password="testpass123",
            role="CUSTOMER"
        )

        self.provider = User.objects.create_user(
            username="payment_provider",
            password="testpass123",
            role="PROVIDER"
        )

        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service="Home Cleaning",
            booking_date=date(2026, 8, 20),
            booking_time=time(11, 30),
            status="PENDING"
        )

        self.webhook_url = "/api/payments/webhook/"

    # =========================================
    # PAYMENT SUCCESS
    # =========================================

    def test_payment_success_confirms_booking(self):

        data = {
            "event": "payment.success",
            "booking_id": self.booking.id,
            "transaction_id": "txn_success_001",
            "amount": "500.00",
        }

        response = self.client.post(
            self.webhook_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            "CONFIRMED"
        )

        payment = Payment.objects.get(
            transaction_id="txn_success_001"
        )

        self.assertEqual(
            payment.status,
            "SUCCESS"
        )

    # =========================================
    # PAYMENT FAILED
    # =========================================

    def test_payment_failed_cancels_booking(self):

        data = {
            "event": "payment.failed",
            "booking_id": self.booking.id,
            "transaction_id": "txn_failed_001",
            "amount": "500.00",
        }

        response = self.client.post(
            self.webhook_url,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.status,
            "CANCELLED"
        )

        payment = Payment.objects.get(
            transaction_id="txn_failed_001"
        )

        self.assertEqual(
            payment.status,
            "FAILED"
        )
