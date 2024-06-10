from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

urlpatterns = [
    path('', views.endpoints),

    path('signup/', views.UserCreateApiView.as_view(), name='signup'),
    path('signin/', views.CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/', views.UserListApiView.as_view(), name='user'),
    path('users/<str:pk>/',
         views.UserRetrieveUpdateDestroyApiView.as_view(), name='user-crud'),
    path('user_profile/', views.UserProfileListApiView.as_view(), name="user-profile"),
    path('user_profile/<str:pk>/',
         views.UserProfileRetriveUpdateDestroyApiView.as_view(), name="user-profile-crud"),

    path('wallets/', views.WalletListApiView.as_view(), name='wallets'),
    path('investment/', views.InvestmentListCreateApiView.as_view(), name='investment'),
    path('investment_sub/', views.InvestmentSubscriptionListCreateApiView.as_view(),
         name='investment_sub'),
    path('transaction/', views.TransactionListCreateApiView.as_view(),
         name="transaction"),
    path('transaction/<str:pk>/',
         views.TransactionRetrieveUpdateDestroyApiView.as_view(), name="transaction-crud")
]
