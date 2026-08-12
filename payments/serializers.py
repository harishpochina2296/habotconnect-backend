from rest_framework import serializers


class PaymentWebhookSerializer(serializers.Serializer):

    event = serializers.ChoiceField(
        choices=[
            "payment.success",
            "payment.failed",
        ]
    )

    booking_id = serializers.IntegerField(
        min_value=1
    )

    transaction_id = serializers.CharField(
        max_length=100
    )

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0
    )