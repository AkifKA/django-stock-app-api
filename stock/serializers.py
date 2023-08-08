
# ? ---------------------------------
# ? FixSerializer
# ? ---------------------------------
from .models import (
    Category,
    Brand,
    Product,
    Firm,
    Purchase,
    Sale,
)
from rest_framework import serializers


class FixSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    user_id = serializers.IntegerField(required=False, read_only=True)

    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user.id
        return super().create(validated_data)


# ? ---------------------------------
# ? Serializers
# ? ---------------------------------


class CategorySerializer(FixSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        exclude = []

    # ? Printing number of products in each object:
    def get_product_count(self, obj):
        return Product.objects.filter(category_id=obj.id).count()


class BrandSerializer(FixSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        exclude = []

    # ? Getting category info from product:
    def get_product_count(self, obj):
        return Product.objects.filter(brand_id=obj.id).count()


class ProductSerializer(FixSerializer):
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()
    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()

    class Meta:
        model = Product
        exclude = []


class FirmSerializer(FixSerializer):

    class Meta:
        model = Firm
        exclude = []


class PurchaseSerializer(FixSerializer):
    firm = serializers.StringRelatedField()
    firm_id = serializers.IntegerField()
    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()
    product = serializers.StringRelatedField()
    product_id = serializers.IntegerField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Purchase
        exclude = []
        read_only_fields = ['price_total']

    # ? Getting category info from product:
    def get_category(self, obj):
        products = Product.objects.filter(id=obj.product_id).values()
        category_id = products[0]['category_id']
        return list(Category.objects.filter(id=category_id).values())


class SaleSerializer(FixSerializer):
    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()
    product = serializers.StringRelatedField()
    product_id = serializers.IntegerField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        exclude = []
        read_only_fields = ['price_total']

    # ? Getting category info from product:
    def get_category(self, obj):
        products = Product.objects.filter(id=obj.product_id).values()
        category_id = products[0]['category_id']
        return list(Category.objects.filter(id=category_id).values())

    # ? Don't sell if you don't have enough in stock:
    def validate(self, data):
        product = Product.objects.get(id=data.get('product_id'))
        if data.get('quantity') > product.stock:
            raise serializers.ValidationError(
                f'Dont have enough stock. Current stock is {product.stock}')

# ? ---------------------------------
# ? Extra Serializers
# ? ---------------------------------
# ? Show products by category (realeted_name):


class CategoryProductsSerializer(CategorySerializer):
    category_products = ProductSerializer(many=True)
