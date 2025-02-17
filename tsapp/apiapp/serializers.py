from rest_framework import serializers
from .models import User, Service, Booking, Technician, Payment,ServiceCategory

# User Registration Serializer
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'user_type']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "phone", "user_type"]  # Add user_type field

    def create(self, validated_data):
        # Validate user_type to be one of the allowed values
        user_type = validated_data.get("user_type", "customer").lower()
        if user_type not in ["customer", "technician", "admin"]:
            raise serializers.ValidationError({"user_type": "Invalid user type"})

        # Create user with the correct type
        return User.objects.create(**validated_data)

# User Profile Serializer (Allows Address Update)
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'user_type', 'address']
        read_only_fields = ['phone', 'user_type']  # Users cannot update phone or role

# Service Serializer
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)  # Get all related services

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'services']

# Booking Serializer

class BookingSerializer(serializers.ModelSerializer):
    technician = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(user_type='technician'),
        required=False,
        allow_null=True  # Allow null if technician is not assigned
    )
    services = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), many=True)

    class Meta:
        model = Booking
        fields = ['id', 'customer', 'services', 'technician', 'service_location', 'status', 'booking_date']
        read_only_fields = ['customer']
class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'user_type', 'address', 'skill_profession']  # ✅ 

# Payment Serializer (Hides Sensitive Fields)
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ['transaction_id']  # Hide sensitive transaction details if needed

class TechnicianRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone', 'location', 'skill_profession', 'user_type']

    def create(self, validated_data):
        validated_data['user_type'] = 'technician'  # Auto-set to technician
        return User.objects.create(**validated_data)