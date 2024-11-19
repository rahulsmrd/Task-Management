from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from task.models import TaskModel
from task.serializers import TaskSerializer, AuthTokenSerializer

TOKEN_URL = reverse('task:token')
TASK_URL = reverse('task:task-list')

def task_detail_url(id):
    return reverse('task:task-detail', args=[id])

def createUser(email='example@gmail.com', password='test@123'):
    return get_user_model().objects.create_user(email=email, password=password)

class TaskTestCase(TestCase):
    def setUp(self) -> None:
        self.user = createUser()
        self.client = APIClient()
        self.client.force_authenticate

    def test_create_task(self):
        user_data = {
            'email': self.user.email,
            'password': 'test@123'
        }
        token = self.client.post(TOKEN_URL, user_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.data.get('token')}')
        task_data = {
            'title': 'Test Task',
            'description': 'This is a test task',
            'status': 'pending',
            'due_date': '2024-12-25',
        }
        response = self.client.post(TASK_URL, task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskModel.objects.count(), 1)
        task_saved = TaskModel.objects.get(**response.data)
        self.assertEqual(task_saved.title, task_data['title'])
        self.assertEqual(task_saved.description, task_data['description'])
        self.assertEqual(task_saved.status, task_data['status'])
        self.assertEqual(task_saved.due_date.strftime('%Y-%m-%d'), task_data['due_date'])
        self.assertEqual(task_saved.user.email, self.user.email)
        self.assertEqual(task_saved.task_id, int(task_saved.task_id))

    def test_update_task(self):
        user_data = {
            'email': self.user.email,
            'password': 'test@123' 
        }
        token = self.client.post(TOKEN_URL, data=user_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.data.get('token')}')
        task_data = {
            'title': 'Test task',
            'description': 'Test task description',
            'status': 'pending',
            'due_date':'2024-12-25',
        }
        response = self.client.post(TASK_URL, data=task_data, format='json')
        task_id = response.data['id']
        url = task_detail_url(task_id)
        patch_update_data = {
            'status': 'completed',
        }
        patch_response = self.client.patch(url, data=patch_update_data)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data.get('status'), patch_update_data['status'])
        put_update_data = {
            'title': 'Test task put',
            'description': 'Test task description put',
            'status': 'in_progress',
            'due_date':'2024-12-25',
        }
        put_response = self.client.put(url, data=put_update_data, format='json')
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.assertEqual(put_response.data.get('status'), put_update_data['status'])
        self.assertEqual(put_response.data.get('title'), put_update_data['title'])
        self.assertEqual(put_response.data.get('description'), put_update_data['description'])

    def test_task_delete(self):
        """Test task delete"""
        user_data = {
            'email': self.user.email,
            'password': 'test@123' 
        }
        token = self.client.post(TOKEN_URL, data=user_data, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.data.get('token')}')
        task_data = {
            'title': 'Test task',
            'description': 'Test task description',
            'status': 'pending',
            'due_date':'2024-12-25',
        }
        response = self.client.post(TASK_URL, data=task_data, format='json')
        task_id = response.data['id']
        url = task_detail_url(task_id)
        delete_response = self.client.delete(url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TaskModel.objects.all().count(), 0)
