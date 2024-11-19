from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from task.models import TaskModel
from task.serializers import UserSerializer

USER_REGISTER = reverse('task:register')
USER_PROFILE = reverse('task:user')
USER_TOKEN = reverse('task:token')

class PrivateUserAPITest(TestCase):
    """Test the private user API"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Test the create_user"""
        data = {
            'email': 'test@example.com',
            'password': 'test123',
            'name': 'Test User'
        }
        response = self.client.post(USER_REGISTER, data, format='json')
        user = get_user_model().objects.get(email=data['email'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], data['email'])
        self.assertTrue(user.check_password(data['password']))

    def test_get_user_profile(self):
        """Test the get_user_profile"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
            name='Test User'
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(USER_PROFILE, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], user.email)
        self.assertEqual(response.data['name'], user.name)
    
    def test_token_response(self):
        """Test token response"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test123',
            name='Test User'
        )
        data = {
            'email': 'test@example.com',
            'password': 'test123'
        }
        self.client.force_authenticate(user=user)
        response = self.client.post(USER_TOKEN, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)