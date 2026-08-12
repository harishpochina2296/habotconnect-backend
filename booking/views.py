from django.db import transaction, IntegrityError
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.models import User

from .models import Booking
from .serializers import BookingSerializer
from .permissions import IsAdmin, IsProvider, IsCustomer


class BookingViewSet(viewsets.ModelViewSet):

    serializer_class = BookingSerializer

    filter_backends = [
        DjangoFilterBackend,
    ]

    filterset_fields = [
        "status",
        "booking_date",
    ]

    # =========================================
    # GET BOOKINGS
    # =========================================

    def get_queryset(self):

        user = self.request.user

        if not user.is_authenticated:
            return Booking.objects.none()

        if user.role == "CUSTOMER":
            return Booking.objects.filter(
                customer=user
            ).select_related(
                "customer",
                "provider"
            )

        if user.role == "PROVIDER":
            return Booking.objects.filter(
                provider=user
            ).select_related(
                "customer",
                "provider"
            )

        if user.role == "ADMIN":
            return Booking.objects.select_related(
                "customer",
                "provider"
            )

        return Booking.objects.none()

    # =========================================
    # PERMISSIONS
    # =========================================

    def get_permissions(self):

        if self.action == "create":
            return [IsCustomer()]

        if self.action == "assign_provider":
            return [IsAdmin()]

        if self.action in ["confirm", "complete"]:
            return [IsProvider()]

        if self.action == "cancel":
            return [IsCustomer()]

        return [IsAuthenticated()]

    # =========================================
    # CREATE BOOKING
    # =========================================

    def perform_create(self, serializer):

        serializer.save(
            customer=self.request.user
        )

    # =========================================
    # ADMIN: ASSIGN PROVIDER
    # =========================================

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdmin]
    )
    def assign_provider(self, request, pk=None):

        booking = self.get_object()

        if booking.status != "PENDING":
            return Response(
                {
                    "error": (
                        "Provider can only be assigned "
                        "to pending bookings."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        provider_id = request.data.get("provider_id")

        if not provider_id:
            return Response(
                {
                    "error": "provider_id is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------
        # FIND PROVIDER
        # -----------------------------------------

        try:
            provider = User.objects.get(
                id=provider_id,
                role="PROVIDER"
            )

        except User.DoesNotExist:
            return Response(
                {
                    "error": "Provider not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -----------------------------------------
        # SAME PROVIDER CHECK
        # -----------------------------------------

        if booking.provider == provider:
            return Response(
                {
                    "error": "This provider is already assigned."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------
        # PROVIDER AVAILABILITY CHECK
        # -----------------------------------------

        existing_booking = Booking.objects.filter(
            provider=provider,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            status__in=[
                "PENDING",
                "CONFIRMED"
            ]
        ).exclude(
            id=booking.id
        ).exists()

        if existing_booking:
            return Response(
                {
                    "error": (
                        "Provider already has a booking "
                        "at this date and time."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------------------
        # ASSIGN PROVIDER
        # -----------------------------------------

        try:

            with transaction.atomic():

                booking.provider = provider
                booking.save(
                    update_fields=[
                        "provider",
                        "updated_at"
                    ]
                )

        except IntegrityError:

            return Response(
                {
                    "error": (
                        "Provider already has a booking "
                        "at this date and time."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK
        )

    # =========================================
    # PROVIDER: CONFIRM BOOKING
    # =========================================

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsProvider]
    )
    def confirm(self, request, pk=None):

        booking = self.get_object()

        if booking.provider != request.user:
            return Response(
                {
                    "error": (
                        "You are not assigned "
                        "to this booking."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if booking.status != "PENDING":
            return Response(
                {
                    "error": (
                        "Only pending bookings "
                        "can be confirmed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = "CONFIRMED"

        booking.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK
        )

    # =========================================
    # PROVIDER: COMPLETE BOOKING
    # =========================================

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsProvider]
    )
    def complete(self, request, pk=None):

        booking = self.get_object()

        if booking.provider != request.user:
            return Response(
                {
                    "error": (
                        "You are not assigned "
                        "to this booking."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if booking.status != "CONFIRMED":
            return Response(
                {
                    "error": (
                        "Only confirmed bookings "
                        "can be completed."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = "COMPLETED"

        booking.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK
        )

    # =========================================
    # CUSTOMER: CANCEL BOOKING
    # =========================================

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsCustomer]
    )
    def cancel(self, request, pk=None):

        booking = self.get_object()

        if booking.customer != request.user:
            return Response(
                {
                    "error": (
                        "You can only cancel "
                        "your own bookings."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if booking.status != "PENDING":
            return Response(
                {
                    "error": (
                        "Only pending bookings "
                        "can be cancelled."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = "CANCELLED"

        booking.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_200_OK
        )