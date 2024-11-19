from django.contrib import admin
from task.models import TaskModel, User

# Register your models here.
admin.site.register(TaskModel)
admin.site.register(User)