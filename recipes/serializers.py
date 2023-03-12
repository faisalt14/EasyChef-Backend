from rest_framework import serializers


from recipes.models import RecipeModel, IngredientModel


class RecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeModel
        fields = ['name', 'difficulty', 'meal', 'cuisine', 'total_reviews', 'total_likes', 'total_favs']

class IngredientSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=RecipeModel.objects.all(), required=False)
    quantity = serializers.IntegerField()
    class Meta:
        model = IngredientModel
        fields = ['id', 'recipe_id', 'name', 'quantity', 'unit']
        extra_kwargs = {
            'quantity': {'required': True}
        }



