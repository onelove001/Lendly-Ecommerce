from django.db import models
from django.conf import settings


class Category(models.Model):
    title = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    image = models.ImageField(upload_to="product_images")
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_id")
    preview_text = models.TextField(max_length=100, verbose_name="Preview Text")
    detailed_text = models.TextField(max_length=500, verbose_name="Description")
    price = models.FloatField()
    old_price = models.FloatField(default=0.00)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-created"]


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = "user_cart")
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default = 1)
    purchase = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.item}"


    def get_total(self):
        return format(self.item.price * self.quantity, '0.2f')


class Order(models.Model):
    order_items = models.ManyToManyField(Cart)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add = True)
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    order_id = models.CharField(max_length=200, blank=True, null=True)


    def __str__(self):
        return self.user.email


    def get_total_amount(self):
        total_amount = 0
        for order in self.order_items.all():
            total_amount += float(order.get_total())
        return total_amount


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.CharField(max_length=250, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.profile.username} Billing Address"


    def is_fully_filled(self):
        field_name = [f.name for f in self._meta.get_fields()]
        for field in field_name:
            value = getattr(self, field)
            if value is None or value == "":
                return False
        return True

    class Meta:
        verbose_name_plural = "Billing Address"