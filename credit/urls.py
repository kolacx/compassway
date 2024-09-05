from django.urls import path, include
from rest_framework.routers import SimpleRouter

from credit.views import ScheduleViewSet, PaymentUpdateView

router = SimpleRouter(trailing_slash=False)

router.register(r'schedule', ScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('schedule/<int:payment_id>/payments', PaymentUpdateView.as_view(), name='payment-update'),
]

