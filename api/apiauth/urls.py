from django.urls import path, include
from .views import RegisterAPIView, LoginAPIView, FarmerAPIView, RefreshAPIView, LogoutAPIView, ForgotAPIView, ResetAPIView, UpdateAPIView, FarmerShortDetailsAPIView, DeleteAPIView, DeleteWorkerAPIView, ContactSupportAPIView, EmployeeAPIView, CoworkersAPIView, PhotoAPIView

urlpatterns = [
    path('register', RegisterAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('farmer', FarmerAPIView.as_view()),
    path('refresh', RefreshAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
    path('forgot', ForgotAPIView.as_view()),
    path('reset', ResetAPIView.as_view()),
    path('update', UpdateAPIView.as_view()),
    path('delete', DeleteAPIView.as_view()),
    path('deleteWorker', DeleteWorkerAPIView.as_view()),
    path('employees', EmployeeAPIView.as_view()),
    path('contactSupport', ContactSupportAPIView.as_view()),
    path('coworkers', CoworkersAPIView.as_view()),
    path('photo', PhotoAPIView.as_view()),
    path('shortDetails', FarmerShortDetailsAPIView.as_view())
]