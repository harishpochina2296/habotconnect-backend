from django.shortcuts import render

from django.db import transaction

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from booking.models import Booking

from .models import Payment
from .serializers import PaymentWebhookSerializer


class PaymentWebhookView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        # -----------------------------------------
        # VALIDATE WEBHOOK PAYLOAD
        # -----------------------------------------

        serializer = PaymentWebhookSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data

        booking_id = data["booking_id"]
        transaction_id = data["transaction_id"]
        amount = data["amount"]
        event = data["event"]

        # -----------------------------------------
        # FIND BOOKING
        # -----------------------------------------

        try:
            booking = Booking.objects.get(
                id=booking_id
            )

        except Booking.DoesNotExist:

            return Response(
                {
                    "error": "Booking not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -----------------------------------------
        # PROCESS PAYMENT + BOOKING UPDATE
        # -----------------------------------------

        try:

            with transaction.atomic():

                payment, created = Payment.objects.get_or_create(
                    transaction_id=transaction_id,
                    defaults={
                        "booking": booking,
                        "amount": amount,
                        "status": "PENDING",
                    }
                )

                # ---------------------------------
                # SUCCESS EVENT
                # ---------------------------------

                if event == "payment.success":

                    payment.status = "SUCCESS"

                    payment.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                    booking.status = "CONFIRMED"

                    booking.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                # ---------------------------------
                # FAILED EVENT
                # ---------------------------------

                elif event == "payment.failed":

                    payment.status = "FAILED"

                    payment.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                    booking.status = "CANCELLED"

                    booking.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

        except Exception:

            return Response(
                {
                    "error": "Unable to process payment webhook."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # -----------------------------------------
        # RESPONSE
        # -----------------------------------------

        return Response(
            {
                "message": "Webhook processed successfully.",
                "payment_status": payment.status,
                "booking_status": booking.status,
                "transaction_id": payment.transaction_id,
            },
            status=status.HTTP_200_OK
        )
