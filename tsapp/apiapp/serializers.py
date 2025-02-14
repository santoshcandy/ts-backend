from rest_framework import serializers
from .models import User, Service, Booking, Technician, Payment

# User Registration Serializer
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone', 'name', 'user_type']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

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

# Booking Serializer
class BookingSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializer(read_only=True)  # To avoid exposing unnecessary details
    technician = serializers.PrimaryKeyRelatedField(queryset=Technician.objects.all(), allow_null=True)

    class Meta:
        model = Booking
        fields = '__all__'

# Technician Serializer (Includes User Details)
class TechnicianSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()  # Fetch technician's associated user details

    class Meta:
        model = Technician
        fields = '__all__'

# Payment Serializer (Hides Sensitive Fields)
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ['transaction_id']  # Hide sensitive transaction details if needed
