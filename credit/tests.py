from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from credit.models import Loan, Payment
from credit.views import ScheduleViewSet


class TestGenerateSchedule(TestCase):
    def test_generate_schedule(self):
        loan = Loan.objects.create(
            amount=Decimal('1000.00'),
            loan_start_date=date(2024, 1, 10),
            number_of_payments=4,
            periodicity='1m',
            interest_rate=Decimal('0.1')
        )

        viewset = ScheduleViewSet()
        payments = viewset.generate_schedule(
            amount=loan.amount,
            loan_start_date=loan.loan_start_date,
            number_of_payments=loan.number_of_payments,
            periodicity=loan.periodicity,
            interest_rate=loan.interest_rate
        )

        expected_payments = [
            {
                'date': date(2024, 2, 10),
                'principal': Decimal('246.90'),
                'interest': Decimal('8.33'),
            },
            {
                'date': date(2024, 3, 10),
                'principal': Decimal('248.95'),
                'interest': Decimal('6.28'),
            },
            {
                'date': date(2024, 4, 10),
                'principal': Decimal('251.03'),
                'interest': Decimal('4.20'),
            },
            {
                'date': date(2024, 5, 10),
                'principal': Decimal('253.12'),
                'interest': Decimal('2.11'),
            }
        ]

        self.assertEqual(len(payments), 4)

        for i, payment in enumerate(payments):
            self.assertAlmostEqual(payment['principal'], expected_payments[i]['principal'], places=2)
            self.assertAlmostEqual(payment['interest'], expected_payments[i]['interest'], places=2)
            self.assertEqual(payment['date'], expected_payments[i]['date'])


class LoanScheduleTests(APITestCase):
    def setUp(self):
        loan = Loan.objects.create(
            amount=Decimal('1000.00'),
            loan_start_date=date(2024, 1, 10),
            number_of_payments=2,
            periodicity='1m',
            interest_rate=Decimal('0.1')
        )

        Payment.objects.create(
            id=1,
            loan=loan,
            date=date(2024, 2, 10),
            principal=Decimal('497.93'),
            interest=Decimal('8.33'),
        )

        Payment.objects.create(
            id=2,
            loan=loan,
            date=date(2025, 3, 10),
            principal=Decimal('502.07'),
            interest=Decimal('4.18'),
        )

    def test_modify_payment(self):
        payment_id = 1
        url = reverse('payment-update', args=[payment_id])

        data = {
            'principal': Decimal('100.00')
        }

        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        payment = Payment.objects.get(id=payment_id)
        self.assertEqual(payment.principal, Decimal('100.00'))
        self.assertTrue(payment.is_fixed)

        following_payment = Payment.objects.get(id=2)
        self.assertAlmostEqual(following_payment.principal, Decimal('900.00'), places=2)
        self.assertAlmostEqual(following_payment.interest, Decimal('7.50'), places=2)
