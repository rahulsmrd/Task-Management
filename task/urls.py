app_name = 'task'

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from task.views import TaskView, CreateUserView, CreateTokenView, ManageUserView, CompleteTaskView



router = DefaultRouter()
router.register('task', TaskView, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('task/<pk>/completed', CompleteTaskView.as_view(), name='completed'),
    path('register/', CreateUserView.as_view(), name='register'),
    path('token/', CreateTokenView.as_view(), name='token'),
    path('user/', ManageUserView.as_view(), name='user'),
]
