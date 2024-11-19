from rest_framework import serializers, status
from rest_framework.response import Response
from datetime import datetime
from django.contrib.auth import authenticate, get_user_model


from.models import TaskModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        user = get_user_model().objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        else:
            raise serializers.ValidationError({'password': 'Password is required.'})
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password',None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={
            'input_type': 'password',
        },
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({'detail': 'Invalid email or password.'})
        attrs['user'] = user
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskModel
        fields = ['id', 'user', 'task_id', 'title', 'description', 'due_date', 'status', 'created_at', 'updated_at',]
        read_only_fields = ['id', 'user','task_id', 'created_at', 'updated_at']

    
    def create(self, validated_data):
        task_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(self.request.user.id)
        validated_data['task_id'] = task_id
        try:
            return TaskModel.objects.create(**validated_data)
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, instance, validated_data, **kwargs):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.updated_at = datetime.now()
        try:
            instance.save()
            return instance
        except Exception as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def validate_due_date(self, value):
        if value < datetime.now().date():
            raise serializers.ValidationError('Due date cannot be in the past.')
        return value
    
    def validate_status(self, value):
        if value not in ['pending', 'in_progress', 'completed']:
            raise serializers.ValidationError('Invalid status.')
        return value