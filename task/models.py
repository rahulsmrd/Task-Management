from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
# Create your models here.

class UserManager(BaseUserManager):

    """Manager for User Model"""

    def create_user(self, email, password=None, **extra_fields):

        """Create Save and Return User Data"""

        if not email:
            raise ValueError("USer must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        if not email:
            raise ValueError("User must have an email address")
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
    
    def create_admin(self, email, password):
        '''Create Admin'''
        if not email:
            raise ValueError("User must have an email address")
        user = self.create_user(email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):

    """User is the system"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    def __str__(self) -> str:
        return str(self.email)


class TaskModel(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'), 
        ('In Progress', 'In Progress'), 
        ('Completed', 'Completed')
    ]
    user = models.ForeignKey(User, related_name='TaskUser', on_delete=models.CASCADE, default=None)
    task_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title