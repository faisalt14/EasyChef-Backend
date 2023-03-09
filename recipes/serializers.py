from rest_framework import serializers
from .models import RecipeModel, RecipeMediaModel, StepModel, StepMediaModel, InteractionModel, ReviewMediaModel, IngredientModel

class RecipeMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeMediaModel
        fields = ['id', 'recipe_id', 'media']

class StepMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepMediaModel
        fields = ['id', 'step_id', 'media']

class StepSerializer(serializers.ModelSerializer):
    media = StepMediaSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = StepModel
        fields = ['id', 'recipe_id', 'step_num', 'cooking_time', 'prep_time', 'instructions', 'media']
        extra_kwargs = {
            'media': {'required': False, 'allow_null': True}
        }

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientModel
        fields = ['id', 'recipe_id', 'name', 'quantity', 'unit']

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InteractionModel
        fields = ['id', 'recipe_id', 'user_id', 'like', 'favourite', 'rating', 'comment', 'published_time']


class ReviewMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewMediaModel
        fields = ['id', 'interaction_id', 'media']

class RecipeSerializer(serializers.ModelSerializer):
    media = RecipeMediaSerializer(many=True, read_only=False)
    steps = StepSerializer(many=True, read_only=False)
    ingredients = IngredientSerializer( many=True, read_only=False)


    class Meta:
        model = RecipeModel
        fields = ['id', 'user_id', 'name', 'based_on', 'total_reviews', 'total_likes', 'total_favs', 'published_time',
                  'difficulty', 'meal', 'diet', 'cuisine', 'cooking_time', 'prep_time', 'servings_num', 'media', 'steps', 'ingredients']

