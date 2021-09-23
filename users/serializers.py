from rest_framework.serializers import ModelSerializer, ReadOnlyField
from .models import UserProfile


class UserProfileSerializer(ModelSerializer):
    
    user = ReadOnlyField(source='user.username')
    
    class Meta:
        model  =  UserProfile
        fields =  '__all__'
