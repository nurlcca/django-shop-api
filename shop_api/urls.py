from django.contrib import admin
from django.urls import path
from users.views import GoogleLoginAPIView, GoogleCallbackAPIView

from product.views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView,
    ProductReviewsAPIView,
    ReviewListCreateAPIView,
    ReviewDetailAPIView,
)

from users.views import (
    RegisterAPIView,
    LoginAPIView,
    ConfirmAPIView,
    CustomTokenObtainPairView,
)


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

    path(
        'api/v1/token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair',
    ),
    
    path("api/v1/users/google/login/", GoogleLoginAPIView.as_view()),
    path("api/v1/users/google/callback/", GoogleCallbackAPIView.as_view()),
]