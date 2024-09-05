from rest_framework import serializers
from .models import Loan, Payment


class LoanSerializer(serializers.ModelSerializer):
    loan_start_date = serializers.DateField(input_formats=["%d-%m-%Y"])

    payments = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = (
            "id",
            "amount",
            "loan_start_date",
            "number_of_payments",
            "periodicity",
            "interest_rate",
            "created_at",
            "payments"
        )

    def get_payments(self, obj):
        payments = Payment.objects.filter(loan=obj)
        return PaymentSerializer(payments, many=True).data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
