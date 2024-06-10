from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *


@receiver(post_save, sender=CustomUser)
def create_user_wallets(sender, instance, created, **kwargs):
    if created:
        # Define the wallet titles and addresses
        wallet_data = [
            {"title": "USDT(TRC20)",
                "wallet_address": "TTPJrqtrR5SipGs6dTkHd7hDRvpXp863id"},
            {"title": "BNB",
                "wallet_address": "0x26D096A992E08133c2fb13ec071D32e951853D45"},
        ]
        # Create a wallet for each entry in wallet_data
        for data in wallet_data:
            Wallet.objects.create(
                user=instance,
                title=data["title"],
                wallet_address=data["wallet_address"],
                balance=0.00
            )


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
