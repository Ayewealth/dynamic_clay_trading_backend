from decimal import Decimal
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.templatetags.static import static
from django.utils.dateformat import DateFormat

from .models import *


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        # Check if the user has a profile_picture before accessing it
        profile_picture = getattr(user, 'profile_picture', None)

        if profile_picture:
            data['profile_picture'] = profile_picture.url

        data['is_superuser'] = user.is_superuser
        data['user_id'] = user.id

        return data


class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'profile_picture',
            'full_name',
            'email',
            'password',
            'is_superuser',
            'date_joined',
        ]
        extra_kwargs = {
            # 'password': {'write_only': True},
            'profile_picture': {'allow_null': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        return user

    def get_date_joined(self, obj):
        # Format the date_joined field as "June 22, 2020"
        return DateFormat(obj.date_joined).format('F j, Y')


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            'id',
            'user',
            'title',
            'wallet_address',
            'balance'
        ]


class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = [
            'id',
            'plan',
            'daily_return_rate',
            'duration_days',
            'minimum_amount',
            'maximum_amount'
        ]


class InvestmentSubscriptionSerializer(serializers.ModelSerializer):
    subscription_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    wallet_title = serializers.SerializerMethodField()
    investment_plan_plan = serializers.SerializerMethodField()

    class Meta:
        model = InvestmentSubscription
        fields = [
            'id',
            'user',
            'investment_plan',
            'investment_plan_plan',
            'wallet',
            'wallet_title',
            'amount',
            'subscription_date',
            'end_date',
            'total_return'
        ]

    def validate(self, data):
        # Retrieve the investment plan and amount from the validated data
        investment_plan = data.get('investment_plan')
        amount = data.get('amount')

        # Retrieve the minimum and maximum amounts allowed for the selected investment plan
        minimum_amount = investment_plan.minimum_amount
        maximum_amount = investment_plan.maximum_amount

        # Check if the amount falls within the range of the minimum and maximum amounts
        if amount < minimum_amount:
            raise ValidationError(
                f'Investment amount cannot be less than {minimum_amount} for the selected plan.')
        if amount > maximum_amount:
            raise ValidationError(
                f'Investment amount cannot exceed {maximum_amount} for the selected plan.')

        return data

    def get_wallet_title(self, obj):
        # Access the title field of the wallet object
        return obj.wallet.title

    def get_investment_plan_plan(self, obj):
        # Access the title field of the wallet object
        return obj.investment_plan.plan

    def get_subscription_date(self, obj):
        # Format the date_joined field as "June 22, 2020"
        return DateFormat(obj.subscription_date).format('F j, Y')

    def get_end_date(self, obj):
        # Format the date_joined field as "June 22, 2020"
        return DateFormat(obj.end_date).format('F j, Y')


class TransactionSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    wallet_title = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_type',
            'user',
            'user_name',
            'wallet',
            'wallet_title',
            'wallet_address',
            'amount',
            'status',
            'date'
        ]

    def get_date(self, obj):
        # Format the date_joined field as "June 22, 2020"
        return DateFormat(obj.date).format('F j, Y')

    def get_wallet_title(self, obj):
        # Access the title field of the wallet object
        return obj.wallet.title

    def get_user_name(self, obj):
        return f"{obj.user.full_name}"


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)
    wallets = serializers.SerializerMethodField()
    transactions = serializers.SerializerMethodField()
    investment = serializers.SerializerMethodField()
    total_wallet_balance = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'user',
            'wallets',
            'transactions',
            'investment',
            'total_wallet_balance'
        ]

    def get_total_wallet_balance(self, user_profile):
        # Get all wallets belonging to the user profile
        wallets = Wallet.objects.filter(user=user_profile.user)
        # Calculate the total balance by summing the balances of all wallets
        total_balance = sum(wallet.balance for wallet in wallets)
        # Return the total balance as a Decimal
        return Decimal(total_balance)

    def get_wallets(self, wallet):
        wallets = Wallet.objects.filter(user=wallet.user)
        return WalletSerializer(wallets, many=True, context=self.context).data

    def get_transactions(self, transactions):
        transactions = Transaction.objects.filter(user=transactions.user)
        return TransactionSerializer(transactions, many=True, context=self.context).data

    def get_investment(self, investment_subscription):
        investment_subscription = InvestmentSubscription.objects.filter(
            user=investment_subscription.user)
        return InvestmentSubscriptionSerializer(investment_subscription, many=True, context=self.context).data
