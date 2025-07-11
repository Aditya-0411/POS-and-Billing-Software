from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from django.contrib.auth.models import User


# SaaS subscription plan model
class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.IntegerField()  # e.g. 30 for monthly
    features = models.TextField(blank=True)

    def __str__(self):
        return self.name


# Store (shop or pharmacy)
class Store(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='store', null=True  # 👈 Make temporarily nullable
    )
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    contact = models.CharField(max_length=100, null=True, blank=True)  #
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


# Custom user model with link to Store and Plan
class User(AbstractUser):
    #store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    subscription_start = models.DateField(null=True, blank=True)
    subscription_end = models.DateField(null=True, blank=True)
    is_active_subscriber = models.BooleanField(default=False)

    def __str__(self):
        return self.username


# Customer model
class Customer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)  # temporarily allow null
    store = models.ForeignKey(Store, on_delete=models.CASCADE,null=False)
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

def __str__(self):
        return self.name


# Product model
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self):
        return self.name


# Invoice model
class Invoice(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Invoice {self.id} - {self.customer.name}"


# Invoice Item model
class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.price