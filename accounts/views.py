from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsCustomer
from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class CustomerDashboardView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        return Response({
            "message": "Welcome Customer",
            "username": request.user.username,
            "role": request.user.role,
        })