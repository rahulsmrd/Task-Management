from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response
from datetime import datetime

from task.models import TaskModel
from task.serializers import TaskSerializer, UserSerializer, AuthTokenSerializer
from task.forms import UserCreateForm, TaskCreationForm

# Create your views here.

def homeView(request):
    return render(request,'task/home.html')

def signupUser(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        if user_form.is_valid():
            user_form.save()
        else:
            return render(request,'task/signup.html', {'form': UserCreateForm, 'errors': UserCreateForm.errors})
        return redirect(reverse('login'))
    return render(request,'task/signup.html', {'form': UserCreateForm()})

def signupAdmin(request):
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        if user_form.is_valid():
            user_form.save(commit=False)
            user_form.instance.is_admin = True
            user_form.save()
        else:
            return render(request,'task/signup.html', {'form': UserCreateForm, 'errors': UserCreateForm.errors})
        return redirect(reverse('login'))
    return render(request,'task/signup.html', {'form': UserCreateForm()})

class LogoutView(auth_views.LogoutView):    
    def get_success_url(self):
        return reverse_lazy('task:login')
    
class TaskListView(ListView, LoginRequiredMixin):
    model = TaskModel
    context_object_name = 'task_list'
    template_name = 'task/tasklist.html'
    def get_queryset(self):
        print('Task list')
        if self.request.user.is_superuser or self.request.user.is_admin:
            self.queryset = TaskModel.objects.all().order_by('-due_date')
        else:
            self.queryset = TaskModel.objects.filter(user = self.request.user).all().order_by('-due_date')
        return super().get_queryset()
    
class DetailTaskView(DetailView, LoginRequiredMixin):
    model = TaskModel
    context_object_name = 'task'
    template_name = 'task/taskdetail.html'
    def get_object(self):
        if self.request.user.is_superuser or self.request.user.is_admin or self.object.user == self.request.user:
            return super().get_object()
        else:
            return HttpResponse("You are not authorized to view this task", status=403)

class CreateTaskView(CreateView, LoginRequiredMixin):
    model = TaskModel
    template_name = 'task/taskcreate.html'
    form_class = TaskCreationForm
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.task_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(form.instance.user.id)
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('task:task_list')
    
class UpdateTaskView(UpdateView, LoginRequiredMixin):
    model = TaskModel
    template_name = 'task/taskupdate.html'
    form_class = TaskCreationForm
    def form_valid(self, form):
        if form.instance.user!= self.request.user:
            return Response({"Error": "You can't update this task"}, status=status.HTTP_403_FORBIDDEN)
        form.instance.updated_at = datetime.now()
        return super().form_valid(form)
    def get_success_url(self) -> str:
        return reverse('task:task_detail', kwargs={'pk': self.object.pk})
    
class DeleteTaskView(DeleteView, LoginRequiredMixin):
    model = TaskModel
    template_name = 'task/taskdelete.html'
    context_object_name = 'delete_task'
    success_url = reverse_lazy('task:task_list')

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