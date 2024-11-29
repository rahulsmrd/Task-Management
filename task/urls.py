app_name = 'task'

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from task.views import TaskView, CreateUserView, CreateTokenView, ManageUserView, CompleteTaskView
from task.views import TaskListView, DetailTaskView, CreateTaskView, UpdateTaskView, DeleteTaskView, signupAdmin, signupUser, LogoutView, homeView



router = DefaultRouter()
router.register('task', TaskView, basename='task')

urlpatterns = [
    path('', homeView, name='home' ),

    path("login/",auth_views.LoginView.as_view(template_name='task/login.html'),name="login"),
    path("logout/",LogoutView.as_view(),name="logout"),
    path("signup/user/",signupUser,name="signupUser"),
    path("signup/admin/",signupAdmin,name="signupAdmin"),

    path('task/list/', TaskListView.as_view(), name='task_list'),
    path('task/<pk>/detail/', DetailTaskView.as_view(), name='task_detail'),
    path('task/create/', CreateTaskView.as_view(), name='create_task'),
    path('task/<pk>/update/', UpdateTaskView.as_view(), name='update_task'),
    path('task/<pk>/delete/', DeleteTaskView.as_view(), name='delete_task'),

    path('api/v1/', include(router.urls)),
    path('api/v1/task/<pk>/completed', CompleteTaskView.as_view(), name='completed'),
    path('api/v1/register/', CreateUserView.as_view(), name='register'),
    path('api/v1/token/', CreateTokenView.as_view(), name='token'),
    path('api/v1/user/', ManageUserView.as_view(), name='user'),
]
