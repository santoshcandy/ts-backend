from django.urls import path
from .views import (
    RegisterView, LoginView, UserProfileView, LogoutView,
      ServiceDetailView, ServiceSearchView,
    BookingCreateView, BookingDetailView, CancelBookingView, RescheduleBookingView,
    TechnicianListView, TechnicianDetailView, AssignTechnicianView,
    InitiatePaymentView, PaymentStatusView, RefundPaymentView,
    AdminBookingListView, AdminUserListView,
    AdminServiceCreateView, AdminServiceUpdateView, AdminServiceDeleteView,
    ServiceByCategoryView,ServiceCategoryListView,TechnicianRegisterView,ProfileView,ProtectedView,
    UserBookingListView, AllUserBookingListView
)

urlpatterns = [
    # 🔹 1️⃣ User Authentication
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),

  path('api/protected/', ProtectedView.as_view(), name='protected'),
    # 🔹 2️⃣ Services
    path("service-categories/", ServiceCategoryListView.as_view(), name="service-category-list"),
    path("services/category/<int:category_id>/", ServiceByCategoryView.as_view(), name="services-by-category"),
    path("services/search/", ServiceSearchView.as_view(), name="service-search"),

    # 🔹 3️⃣ Bookings
    path("bookings/create/", BookingCreateView.as_view(), name="booking-create"),
    path("bookings/", UserBookingListView.as_view(), name="user-booking-list"), 
    path("bookings/all", AllUserBookingListView.as_view(), name="all-booking-list"), 

    path("bookings/<int:pk>/", BookingDetailView.as_view(), name="booking-detail"),
    path("bookings/<int:pk>/cancel/", CancelBookingView.as_view(), name="booking-cancel"),
    path("bookings/<int:pk>/reschedule/", RescheduleBookingView.as_view(), name="booking-reschedule"),

    # 🔹 4️⃣ Technicians
    # 🔹 Technician Authentication APIs
    path("auth/technician/register/", TechnicianRegisterView.as_view(), name="technician-register"),
    path("auth/technician/login/", LoginView.as_view(), name="technician-login"),

    path("technicians/", TechnicianListView.as_view(), name="technician-list"),
    path("technicians/<int:pk>/", TechnicianDetailView.as_view(), name="technician-detail"),
    path("bookings/<int:pk>/assign-technician/", AssignTechnicianView.as_view(), name="assign-technician"),

    # 🔹 5️⃣ Payments
    path("payments/initiate/", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("payments/<int:pk>/", PaymentStatusView.as_view(), name="payment-status"),
    path("payments/<int:pk>/refund/", RefundPaymentView.as_view(), name="refund-payment"),

    # 🔹 6️⃣ Admin APIs (Restricted)
    path("admin/bookings/", AdminBookingListView.as_view(), name="admin-bookings"),
    path("admin/users/", AdminUserListView.as_view(), name="admin-users"),
    path("admin/services/create/", AdminServiceCreateView.as_view(), name="admin-service-create"),
    path("admin/services/<int:pk>/update/", AdminServiceUpdateView.as_view(), name="admin-service-update"),
    path("admin/services/<int:pk>/delete/", AdminServiceDeleteView.as_view(), name="admin-service-delete"),
]
