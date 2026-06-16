from rest_framework import serializers

from .models import Category, Product, Review
from common.validators import validate_user_age_from_token


class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']

    def validate_name(self, name):
        if len(name) < 2:
            raise serializers.ValidationError(
                "Category name must be at least 2 characters."
            )
        return name


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category']

    def validate(self, attrs):
        request = self.context.get("request")

        if request and request.method == "POST":
            validate_user_age_from_token(request)

        return attrs

    def validate_title(self, title):
        if len(title) < 2:
            raise serializers.ValidationError(
                "Product title must be at least 2 characters."
            )
        return title

    def validate_description(self, description):
        if len(description) < 5:
            raise serializers.ValidationError(
                "Description must be at least 5 characters."
            )
        return description

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError(
                "Price must be greater than 0."
            )
        return price


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'text', 'stars', 'product']

    def validate_text(self, text):
        if len(text) < 5:
            raise serializers.ValidationError(
                "Review text must be at least 5 characters."
            )
        return text

    def validate_stars(self, stars):
        if stars < 1 or stars > 5:
            raise serializers.ValidationError(
                "Stars must be from 1 to 5."
            )
        return stars


class ProductReviewsSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'price',
            'category',
            'reviews',
            'rating'
        ]