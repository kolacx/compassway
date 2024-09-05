from decimal import Decimal

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Loan, Payment
from .serializers import LoanSerializer, PaymentSerializer
from datetime import timedelta
from dateutil.relativedelta import relativedelta


PERIODICITY_MAP = {
            'd': {
                'timedelta': timedelta(days=1),
                'period': Decimal(7) / Decimal(365)
            },
            'w': {
                'timedelta': timedelta(weeks=1),
                'period': Decimal(1) / Decimal(52)
            },
            'm': {
                'timedelta': relativedelta(months=1),
                'period': Decimal(1) / Decimal(12)
            },
            'y': {
                'timedelta': relativedelta(years=1),
                'period': Decimal(6) / Decimal(12)
            }
        }


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loan = serializer.save()

        payments = self.generate_schedule(
            amount=loan.amount,
            loan_start_date=loan.loan_start_date,
            number_of_payments=loan.number_of_payments,
            periodicity=loan.periodicity,
            interest_rate=loan.interest_rate
        )

        Payment.objects.bulk_create(
            [Payment(loan=loan, **payment) for payment in payments]
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def generate_schedule(self, amount, loan_start_date, number_of_payments, periodicity, interest_rate):
        payments = []

        interval = int(periodicity[:-1]) * PERIODICITY_MAP[periodicity[-1]]['timedelta']
        percent_periodicity = PERIODICITY_MAP[periodicity[-1]]['period']

        P = amount
        r = interest_rate
        l = percent_periodicity
        i = r * l
        n = number_of_payments

        emi = (i * P) / (1 - (1 + i) ** -n)

        balance = P
        for idx in range(1, number_of_payments + 1):
            interest_payment = balance * i
            principal_payment = emi - interest_payment
            payment_date = loan_start_date + interval * idx

            payments.append({
                'date': payment_date,
                'principal': principal_payment,
                'interest': interest_payment,
            })

            balance -= principal_payment

        return payments


class PaymentUpdateView(APIView):
    def put(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if payment.is_fixed:
            return Response({"error": "Payment is already fixed"}, status=status.HTTP_400_BAD_REQUEST)

        new_principal = request.data.get("principal")
        if new_principal is not None:
            payment.principal = new_principal
            payment.is_fixed = True
            payment.interest = payment.loan.interest_rate * payment.loan.amount / payment.loan.number_of_payments  # Розрахунок нових відсотків
            payment.save()

            self.update_following_payments(payment)

            return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
        return Response({"error": "No principal amount provided"}, status=status.HTTP_400_BAD_REQUEST)

    def update_following_payments(self, modified_payment):
        loan = modified_payment.loan
        payments = loan.payments.filter(id__gt=modified_payment.id).order_by('date')

        balance = loan.amount - sum(p.principal for p in loan.payments.filter(id__lte=modified_payment.id))

        r = loan.interest_rate
        l = PERIODICITY_MAP[loan.periodicity[-1]]['period']
        i = r * l
        n = len(payments)

        if n > 0:
            emi = (i * balance) / (Decimal('1') - (Decimal('1') + i) ** -n)
        else:
            emi = Decimal('0.00')

        for payment in payments:
            if not payment.is_fixed:
                interest_payment = balance * i
                principal_payment = emi - interest_payment

                payment.principal = principal_payment
                payment.interest = interest_payment
                payment.save()

                balance -= principal_payment

