from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(Investment)
admin.site.register(InvestmentSubscription)
