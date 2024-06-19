from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *

# Create your views here.


@api_view(['Get'])
def endpoints(request):
    data = [
        '/signup',
        '/signin',
        '/token/refresh',
        '/users',
        '/users/:id',
        '/wallets',
        '/investment_sub'
    ]
    return Response(data)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class UserCreateApiView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class UserListApiView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer



class UserRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Exclude 'password' from the request data
        fields_to_exclude = []

        # Include all other fields in the request data
        request_data = {
            key: value for key, value in request.data.items()
            if key not in fields_to_exclude
        }

        # Check if the image fields are provided in the request data
        if 'profile_picture' in request.data:
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                # Update the profile picture if provided
                request_data['profile_picture'] = profile_picture
            else:
                # Retain the existing profile picture
                request_data['profile_picture'] = instance.profile_picture

        serializer = self.get_serializer(
            instance, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileListApiView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileRetriveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'pk'


class WalletListApiView(generics.ListAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class WalletRetriveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    lookup_field = 'pk'



class InvestmentListCreateApiView(generics.ListCreateAPIView):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer


class InvestmentSubscriptionListCreateApiView(generics.ListCreateAPIView):
    queryset = InvestmentSubscription.objects.all()
    serializer_class = InvestmentSubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        wallet_id = data.get('wallet')
        investment_plan_id = data.get('investment_plan')
        amount = data.get('amount')

        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet does not exist or does not belong to the current user"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            investment_plan = Investment.objects.get(id=investment_plan_id)
        except Investment.DoesNotExist:
            return Response({"error": "Investment plan does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        amount_decimal = Decimal(amount)
        if wallet.balance < amount_decimal:
            return Response({"error": "Insufficient balance in the wallet"}, status=status.HTTP_400_BAD_REQUEST)

        wallet.balance -= amount_decimal
        wallet.save()

        investment_subscription_data = {
            'user': request.user.id,
            'wallet': wallet_id,
            'investment_plan': investment_plan_id,
            'amount': amount
        }
        serializer = self.get_serializer(data=investment_subscription_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionListCreateApiView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        wallet_id = data.get('wallet')
        amount = data.get('amount')
        transaction_type = data.get('transaction_type')
        wallet_address = data.get('wallet_address')
        transaction_status = data.get('status')

        try:
            wallet = Wallet.objects.get(id=wallet_id, user=request.user)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet does not exist or does not belong to the current user"}, status=status.HTTP_400_BAD_REQUEST)

        amount_decimal = Decimal(amount)
        if amount_decimal <= Decimal(0):
            return Response({"error": "Transaction amount must be greater than zero"}, status=status.HTTP_400_BAD_REQUEST)

        if transaction_type == 'withdrawal' and wallet.balance < amount_decimal:
            return Response({"error": "Insufficient funds in the wallet"}, status=status.HTTP_400_BAD_REQUEST)

        if transaction_status == 'done' and transaction_type == 'deposit':
            wallet.balance += amount_decimal
            wallet.save()
        elif transaction_status == 'done' and transaction_type == 'withdrawal':
            wallet.balance -= amount_decimal
            wallet.save()

        transaction_data = {
            'user': request.user.id,
            'wallet': wallet_id,
            'amount': amount_decimal,
            'status': transaction_status,
            'transaction_type': transaction_type,
            'wallet_address': wallet_address
        }
        serializer = self.get_serializer(data=transaction_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionRetrieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    lookup_field = "pk"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        old_status = instance.status
        new_status = request.data.get('status', old_status)

        if new_status != old_status:
            if new_status == 'done' and instance.transaction_type == 'deposit':
                wallet = instance.wallet
                amount = instance.amount
                wallet.balance += amount
                wallet.save()
            elif new_status == "done" and instance.transaction_type == "withdrawal":
                wallet = instance.wallet
                amount = instance.amount
                wallet.balance -= amount
                wallet.save()

        self.perform_update(serializer)
        return Response(serializer.data)
