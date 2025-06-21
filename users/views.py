# Dosya: users/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import UserCreateSerializer, UserDetailSerializer, UserListSerializer
from .models import CustomUser

class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'
    def get_serializer_context(self):
        return {'request': self.request}

class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return CustomUser.objects.exclude(pk=self.request.user.pk)
    def get_serializer_context(self):
        return {'request': self.request}

class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        response_serializer = UserDetailSerializer(user, context={'request': request})
        response_data = response_serializer.data
        response_data['token'] = token.key
        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user
    def get_serializer_context(self):
        return {'request': self.request}