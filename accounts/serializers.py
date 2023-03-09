from rest_framework import serializers
from accounts.models import User
from rest_framework.response import Response

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'phone_num']
    
    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['username'], password=validated_data['password'], email=validated_data['email'], first_name=validated_data['first_name'], last_name=validated_data['last_name'], phone_num=validated_data['phone_num'])
        user.save()
        return Response({'message': 'success'}, status=200)

class UserLoginSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['username', 'password']

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'email', 'first_name', 'last_name', 'phone_num', 'avatar']
        