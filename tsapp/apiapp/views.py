from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Service, Booking, Payment
from .serializers import (
    UserProfileSerializer, ServiceSerializer, BookingSerializer,
    PaymentSerializer, UserRegisterSerializer, TechnicianSerializer
)

# 🔹 1️⃣ User Authentication & Management APIs

class RegisterView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        user = get_object_or_404(User, phone=phone)

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserProfileSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully!"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

# 🔹 2️⃣ Service Listings & Search API

class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceDetailView(generics.RetrieveAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceSearchView(generics.ListAPIView):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        query = self.request.query_params.get("query", "")
        return Service.objects.filter(name__icontains=query)

# 🔹 3️⃣ Booking & Scheduling API

class BookingCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class BookingDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

class CancelBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        booking = get_object_or_404(Booking, id=pk, customer=request.user)
        booking.status = "cancelled"
        booking.save()
        return Response({"message": "Booking cancelled successfully!"}, status=status.HTTP_200_OK)

class RescheduleBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk):
        booking = get_object_or_404(Booking, id=pk, customer=request.user)
        new_date = request.data.get("new_date")
        if new_date:
            booking.booking_date = new_date
            booking.status = "pending"
            booking.save()
            return Response({"message": "Booking rescheduled successfully!"}, status=status.HTTP_200_OK)
        return Response({"error": "New date is required"}, status=status.HTTP_400_BAD_REQUEST)

# 🔹 4️⃣ Technician Management API

class TechnicianListView(generics.ListAPIView):
    queryset = User.objects.filter(user_type="technician")
    serializer_class = TechnicianSerializer

class TechnicianDetailView(generics.RetrieveAPIView):
    queryset = User.objects.filter(user_type="technician")
    serializer_class = TechnicianSerializer

class AssignTechnicianView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        booking = get_object_or_404(Booking, id=pk)
        technician_id = request.data.get("technician_id")
        technician = get_object_or_404(User, id=technician_id, user_type="technician")

        booking.technician = technician
        booking.status = "confirmed"
        booking.save()

        return Response({"message": "Technician assigned successfully!"}, status=status.HTTP_200_OK)

# 🔹 5️⃣ Payment & Transactions API

class InitiatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()
            return Response({"message": "Payment initiated", "payment_id": payment.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentStatusView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class RefundPaymentView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, pk):
        payment = get_object_or_404(Payment, id=pk)
        payment.status = "refunded"
        payment.save()
        return Response({"message": "Refund processed"}, status=status.HTTP_200_OK)

# 🔹 6️⃣ Admin Dashboard API (Restricted to Admins)

class AdminBookingListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

class AdminUserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

class AdminServiceCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ServiceSerializer

class AdminServiceUpdateView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class AdminServiceDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
