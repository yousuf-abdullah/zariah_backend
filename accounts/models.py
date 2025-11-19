from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model.

    For now, we keep username as-is (from AbstractUser) to keep auth simple,
    but we add fields we know we'll need later.
    """

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_kyc_bypassed = models.BooleanField(default=False)

    def __str__(self):
        return self.username or f"User {self.pk}"


class KYCProfile(models.Model):
    """
    Stores KYC information for each user.
    We’ll expand fields later as needed (CNIC, address, etc.).
    """

    class KYCStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="kyc_profile",
    )
    cnic = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=KYCStatus.choices,
        default=KYCStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"KYC for {self.user}"
