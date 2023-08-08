
# ? ---------------------------------
# ? FixModel
# ? ---------------------------------
from django.db import models
from django.contrib.auth.models import User


class FixModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# ? ---------------------------------
# ? Models
# ? ---------------------------------


class Category(FixModel):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Brand(FixModel):
    name = models.CharField(max_length=64, unique=True)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(FixModel):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='category_products')
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name='brand_products')
    name = models.CharField(max_length=128, unique=True)
    stock = models.SmallIntegerField(blank=True, default=0)

    def __str__(self):
        return f'{self.category} - {self.brand} - {self.name} # {self.stock}'


class Firm(FixModel):
    name = models.CharField(max_length=64)
    phone = models.CharField(max_length=16, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'{self.name} {self.phone}'


class Purchase(FixModel):
    firm = models.ForeignKey(
        Firm, on_delete=models.SET_NULL, null=True, related_name='firm_purchases')
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name='brand_purchases')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_purchases')
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    price_total = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'{self.product} [+{self.quantity}]'

    # ? insert/update:
    def save(self, *args, **kwargs):
        if (self.id):  # ? update
            old_quantity = Purchase.objects.get(id=self.id).quantity
            new_quantity = self.quantity - old_quantity
        else:  # ? insert
            new_quantity = self.quantity
         # ? Getting product:
        product = Product.objects.get(id=self.product_id)
        # ? Updating product stock information:
        product.stock += new_quantity
        # ? Saving product:
        product.save()
        return super().save(*args, **kwargs)

    # delete:
    def delete(self, *args, **kwargs):
        # ? Getting product:
        product = Product.objects.get(id=self.product_id)
        # ? Updating product stock information:
        product.stock -= self.quantity
        # ? Saving product:
        product.save()
        return super().delete(*args, **kwargs)


class Sale(FixModel):
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name='brand_sales')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_sales')
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    price_total = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'{self.product} [-{self.quantity}]'

    # ? insert/update:
    def save(self, *args, **kwargs):
        if (self.id):  # ? update
            old_quantity = Sale.objects.get(id=self.id).quantity
            new_quantity = self.quantity - old_quantity
        else:  # ? insert
            new_quantity = self.quantity
        # ? Getting product:
        product = Product.objects.get(id=self.product_id)
        # ? Is the quantity enough?
        if (product.stock >= new_quantity):
            # ? Enough:
            # ? Updating product stock information:
            product.stock -= new_quantity
            # ? Save Product:
            product.save()
            return super().save(*args, **kwargs)
        else:
            # ? Not Enough:
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f'Dont have enough stock. Current stock is {product.stock}')

    # ?delete:
    def delete(self, *args, **kwargs):
        # ? Getting product:
        product = Product.objects.get(id=self.product_id)
        # ? Updating product stock information:
        product.stock += self.quantity
        # ? Saving product:
        product.save()
        return super().delete(*args, **kwargs)
