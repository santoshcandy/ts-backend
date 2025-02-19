from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Service, Booking, Payment,ServiceCategory
from .serializers import (
    UserProfileSerializer, ServiceSerializer, BookingSerializer,
    PaymentSerializer, UserRegisterSerializer, TechnicianSerializer,
     ServiceCategorySerializer,TechnicianRegisterSerializer,RegisterSerializer
)
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication

# 🔹 1️⃣ User Authentication & Management APIs

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": f"{user.user_type.capitalize()} registered successfully!",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "phone": user.phone,
                    "user_type": user.user_type
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        user = get_object_or_404(User, phone=phone)

        refresh = RefreshToken.for_user(user)
        
        # Generate the access and refresh tokens
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "user": {
                "id": user.id,
                "phone": user.phone,
                "name": user.name,
                "user_type": user.user_type,
            },
            "access": access_token,
            "refresh": refresh_token
        }, status=status.HTTP_200_OK)
    

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserProfileSerializer

    def get_object(self):
        print("Request User:", self.request.user)  # Debugging line
        return self.request.user

class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Profile fetched successfully",
            "user": {
                "id": request.user.id,
                "name": request.user.name,
                "phone": request.user.phone,
                "user_type": request.user.user_type,
                "address": request.user.address,
            }
        })
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

class ServiceCategoryListView(generics.ListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer

# Get Services by Category (All services inside a category)
class ServiceByCategoryView(generics.ListAPIView):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Service.objects.filter(category_id=category_id)
    
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
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        # Automatically set the customer to the authenticated user
        booking = serializer.save(customer=self.request.user)
        
        # If the request contains services, associate them with the booking
        if 'services' in self.request.data:
            services = self.request.data['services']
            booking.services.set(services)  # Add multiple services to the booking
            booking.save()


 

 

# User = get_user_model()

# class BookingCreateView(generics.CreateAPIView):
#     permission_classes = [AllowAny]  # Allow booking without login
#     serializer_class = BookingSerializer

#     def post(self, request, *args, **kwargs):
#         phone = request.data.get("phone")
#         if not phone:
#             return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

#         # Log incoming request for debugging
#         print("Received booking request:", request.data)

#         # Check if the user exists
#         user = User.objects.filter(phone=phone).first()
#         if not user:
#             # If user doesn't exist, register them
#             user = User.objects.create(phone=phone, user_type="customer")
#             user.set_unusable_password()
#             user.save()

#         # Generate tokens
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh.access_token)

#         # Validate and create booking
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(customer=user)  # Assign booking to user
#             return Response({
#                 "message": "Booking successful",
#                 "booking": serializer.data,
#                 "access_token": access_token
#             }, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BookingDetailView(generics.RetrieveAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the authenticated user and filter bookings for this user
        user = self.request.user
        return Booking.objects.filter(customer=user)
    
class UserBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the authenticated user and filter bookings for this user
        user = self.request.user
        return Booking.objects.filter(customer=user)
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


class AllUserBookingListView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all().order_by('-booking_date')

# 🔹 4️⃣ Technician Management API


class TechnicianListView(generics.ListAPIView):
    serializer_class = TechnicianSerializer

    def get_queryset(self):
        return User.objects.filter(user_type="technician") 

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

class TechnicianRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = TechnicianRegisterSerializer
    permission_classes = [AllowAny]  



class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Token is valid!", "user": str(request.user)})