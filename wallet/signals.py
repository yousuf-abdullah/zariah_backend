from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import Wallet


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    """
    Automatically create a gold wallet whenever a new user is created.
    """
    if created:
        Wallet.objects.create(user=instance)
