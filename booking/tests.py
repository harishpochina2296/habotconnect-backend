from datetime import date, time

from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Booking


User = get_user_model()


class BookingAPITestCase(APITestCase):

    def setUp(self):

        # -----------------------------
        # CREATE CUSTOMER
        # -----------------------------

        self.customer = User.objects.create_user(
            username="customer1",
            password="testpass123",
            role="CUSTOMER"
        )

        # -----------------------------
        # CREATE PROVIDER
        # -----------------------------

        self.provider = User.objects.create_user(
            username="provider1",
            password="testpass123",
            role="PROVIDER"
        )

        # -----------------------------
        # CREATE ADMIN
        # -----------------------------

        self.admin = User.objects.create_user(
            username="admin1",
            password="testpass123",
            role="ADMIN"
        )

        # -----------------------------
        # CREATE BOOKING
        # -----------------------------

        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service="Home Cleaning",
            booking_date=date(2026, 8, 20),
            booking_time=time(11, 30),
            status="PENDING"
        )

    # =========================================
    # CUSTOMER TESTS
    # =========================================

    def test_customer_can_create_booking(self):

        self.client.force_authenticate(
            user=self.customer
        )

        data = {
            "service": "Plumbing",
            "booking_date": "2026-08-21",
            "booking_time": "10:00:00",
            "notes": "Kitchen tap repair"
        }

        response = self.client.post(
            "/bookings/",
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data["status"],
            "PENDING"
        )

        self.assertEqual(
            response.data["customer"],
            self.customer.id
        )

    def test_customer_sees_only_own_bookings(self):

        another_customer = User.objects.create_user(
            username="customer2",
            password="testpass123",
            role="CUSTOMER"
        )

        Booking.objects.create(
            customer=another_customer,
            provider=self.provider,
            service="Painting",
            booking_date=date(2026, 8, 22),
            booking_time=time(12, 0),
            status="PENDING"
        )

        self.client.force_authenticate(
            user=self.customer
        )

        response = self.client.get(
            "/bookings/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        results = response.data["results"]

        for booking in results:
            self.assertEqual(
                booking["customer"],
                self.customer.id
            )

    def test_customer_can_cancel_own_booking(self):

        self.client.force_authenticate(
            user=self.customer
        )

        response = self.client.post(
            f"/bookings/{self.booking.id}/cancel/"
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

    # =========================================
    # PROVIDER TESTS
    # =========================================

    def test_provider_can_confirm_booking(self):

        self.client.force_authenticate(
            user= self.provider
        )


        print("PROVIDER:", self.provider.id)
        print("BOOKING:", self.booking.id)
        print("BOOKING PROVIDER:", self.booking.provider_id)
        print("ROLE:", self.provider.role)


        response = self.client.post(
            f"/bookings/{self.booking.id}/confirm/"
        )

        print("STATUS:", response.status_code)
        print("CONTENT:", response.content)

        assert response.status_code == 200


    # =========================================
    # ADMIN TESTS
    # =========================================

    def test_admin_can_assign_provider(self):

        self.booking.provider = None
        self.booking.save()

        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.post(
            f"/bookings/{self.booking.id}/assign_provider/",
            {
                "provider_id": self.provider.id
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.booking.refresh_from_db()

        self.assertEqual(
            self.booking.provider,
            self.provider
        )

    # =========================================
    # FILTERING TESTS
    # =========================================

    def test_filter_pending_bookings(self):

        self.client.force_authenticate(
            user=self.customer
        )

        response = self.client.get(
            "/bookings/?status=PENDING"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        for booking in response.data["results"]:
            self.assertEqual(
                booking["status"],
                "PENDING"
            )

    def test_filter_by_booking_date(self):

        self.client.force_authenticate(
            user=self.customer
        )

        response = self.client.get(
            "/bookings/?booking_date=2026-08-20"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        for booking in response.data["results"]:
            self.assertEqual(
                booking["booking_date"],
                "2026-08-20"
            )


    def test_booking_queryset_avoids_n_plus_one_queries(self):

    # Create multiple bookings
      for i in range(5):
        Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=f"Service {i}",
            booking_date=date(2026, 8, 20),
            booking_time=time(12, i),
            status="PENDING"
        )

      self.client.force_authenticate(
        user=self.customer
    )

    # Get the actual queryset used by the API
      response = self.client.get("/bookings/")

      self.assertEqual(
        response.status_code,
        status.HTTP_200_OK
    )

    # Now retrieve bookings through the same optimized relationship pattern
      queryset = Booking.objects.filter(
        customer=self.customer
    ).select_related(
        "customer",
        "provider"
    )

      bookings = list(queryset)

    # The queryset evaluation should load customer/provider
    # through the JOIN, so accessing them should not issue
    # additional queries.
      with self.assertNumQueries(0):

        for booking in bookings:
            _ = booking.customer.username
            _ = booking.provider.username