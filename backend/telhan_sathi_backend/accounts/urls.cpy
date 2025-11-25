from django.urls import path
from .views import generate_otp, verify_otp

urlpatterns = [
    path('generate-otp/', generate_otp),
    path('verify-otp/', verify_otp),
]
