from django.db import models


class Loan(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_start_date = models.DateField()
    number_of_payments = models.PositiveIntegerField()
    periodicity = models.CharField(max_length=3)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class Payment(models.Model):
    loan = models.ForeignKey(Loan, related_name='payments', on_delete=models.CASCADE)
    date = models.DateField()
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    interest = models.DecimalField(max_digits=10, decimal_places=2)
    is_fixed = models.BooleanField(default=False)
