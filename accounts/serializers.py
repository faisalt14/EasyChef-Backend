from rest_framework import serializers
from accounts.models import User, ShoppingRecipeModel
from rest_framework.response import Response

from recipes.models import RecipeModel


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'phone_num']

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data.get('username'),
                                        password=validated_data.get('password'),
                                        email=validated_data.get('email', ''),
                                        first_name=validated_data.get('first_name', ''),
                                        last_name=validated_data.get('last_name', ''),
                                        phone_num=validated_data.get('phone_num', ''))
        user.save()
        return Response({'message': 'success'}, status=200)

class UserDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

class UserLoginSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password', 'email', 'first_name', 'last_name', 'phone_num', 'avatar']
        extra_kwargs = {
            'password': {'required': False}
        }


class ShoppingRecipeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingRecipeModel
        fields = ['recipe_id', 'servings_num']
