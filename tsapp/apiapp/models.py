from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, phone, name, user_type="customer"):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, name=name, user_type=user_type)
        user.set_unusable_password()  # No password needed
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name):
        user = self.create_user(phone, name, user_type="admin")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# User Model
class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('technician', 'Technician'),
        ('admin', 'Admin'),
    )
    
    phone = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')

    # Address - Optional at registration, required for booking
    address = models.TextField(null=True, blank=True)

    # Required fields for Django User model compatibility
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name"]

    # Fix for Django auth system clashes
    groups = models.ManyToManyField(
        "auth.Group", related_name="custom_user_groups", blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="custom_user_permissions", blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.phone})"

# Service Model
class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

# Booking Model (Fixing reverse accessor clashes)
class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="customer_bookings",
        limit_choices_to={'user_type': 'customer'}
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    technician = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="technician_bookings", limit_choices_to={'user_type': 'technician'}
    )
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Customer Address at time of Booking
    service_location = models.TextField()

    def __str__(self):
        return f"Booking {self.id} - {self.service.name} for {self.customer.name}"

# Technician Model
class Technician(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="technician_profile",
        limit_choices_to={'user_type': 'technician'}
    )
    skills = models.TextField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.name

# Payment Model
class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('failed', 'Failed'),
    )
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
