from django.db import models

class Farmer(models.Model):
    farmer_id = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    district = models.CharField(max_length=50)
    land_size = models.FloatField(help_text="Acres of land")

    def __str__(self):
        return f"{self.name} ({self.farmer_id})"

class OTP(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.farmer.farmer_id}"
