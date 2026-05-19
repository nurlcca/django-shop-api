"""
URL configuration for shop_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from product.views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView,
    ProductReviewsAPIView,
    ReviewListCreateAPIView,
    ReviewDetailAPIView
)
from users.views import RegisterAPIView, LoginAPIView, ConfirmAPIView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/categories/', CategoryListCreateAPIView.as_view()),
    path('api/v1/categories/<int:id>/', CategoryDetailAPIView.as_view()),

    path('api/v1/products/', ProductListCreateAPIView.as_view()),
    path('api/v1/products/<int:id>/', ProductDetailAPIView.as_view()),
    path('api/v1/products/reviews/', ProductReviewsAPIView.as_view()),

    path('api/v1/reviews/', ReviewListCreateAPIView.as_view()),
    path('api/v1/reviews/<int:id>/', ReviewDetailAPIView.as_view()),

    path('api/v1/users/register/', RegisterAPIView.as_view()),
    path('api/v1/users/login/', LoginAPIView.as_view()),
    path('api/v1/users/confirm/', ConfirmAPIView.as_view()),
]