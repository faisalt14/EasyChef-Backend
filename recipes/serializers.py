from rest_framework import serializers


from recipes.models import RecipeModel


class RecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeModel
        fields = ['name', 'difficulty', 'meal', 'cuisine', 'total_reviews', 'total_likes', 'total_favs']


