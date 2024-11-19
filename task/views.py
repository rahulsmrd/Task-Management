from django.shortcuts import render
from rest_framework import viewsets, status, generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from datetime import datetime

from task.models import TaskModel
from task.serializers import TaskSerializer, UserSerializer, AuthTokenSerializer

# Create your views here.

class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch']
    def update(self, request, *args, **kwargs):
        data = request.data
        if 'email' in data:
            return Response({"Error": "You can't update an authenticated Email"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

class TaskView(viewsets.ModelViewSet):
    queryset = TaskModel.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']

    def get_queryset(self):
        if self.request.user.is_superuser:
            self.queryset = TaskModel.objects.all()
        else:
            self.queryset = TaskModel.objects.filter(user = self.request.user).all()
        return super().get_queryset()
    
    def create(self, request):
        data = request.data
        data['due_date'] = datetime.strptime(data['due_date'], "%Y-%m-%d" ).date()
        data['user'] = self.request.user.id

        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk, **kwargs):
        task = TaskModel.objects.get(pk=pk)
        if task.user!= self.request.user:
            return Response({'error': 'You are not authorized to update this task.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        if 'due_date' in data:
            data['due_date'] = datetime.strptime(data['due_date'], "%Y-%m-%d" ).date()
        data['user'] = self.request.user.id
        serializer = TaskSerializer(task, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        task = TaskModel.objects.get(pk=pk)
        if task.user!= self.request.user:
            return Response({'error': 'You are not authorized to delete this task.'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response({'Message': "Deleted Successfully..."}, status=status.HTTP_204_NO_CONTENT)

class CompleteTaskView(generics.UpdateAPIView):
    queryset = TaskModel.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def update(self, request, pk, **kwargs):
        task = TaskModel.objects.get(pk=pk)
        if task.user!= self.request.user:
            return Response({'error': 'You are not authorized to update this task.'}, status=status.HTTP_403_FORBIDDEN)
        data = {"status": "completed"}
        serializer = TaskSerializer(task, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)