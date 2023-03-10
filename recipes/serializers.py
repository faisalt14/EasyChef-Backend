from rest_framework import serializers
from .models import RecipeModel, RecipeMediaModel, StepModel, StepMediaModel, InteractionModel, ReviewMediaModel, IngredientModel

class RecipeMediaSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=RecipeModel.objects.all(), required=False)
    class Meta:
        model = RecipeMediaModel
        fields = ['id', 'recipe_id', 'media']

class StepMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = StepMediaModel
        fields = ['id', 'step_id', 'media']
        extra_kwargs = {
            'media': {'required': True}
        }


class StepSerializer(serializers.ModelSerializer):
    media = StepMediaSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = StepModel
        fields = ['id', 'recipe_id', 'step_num', 'cooking_time', 'prep_time', 'instructions', 'media']
        extra_kwargs = {
            'media': {'required': False, 'allow_null': True}
        }

    def create(self, validated_data):
        media_data = validated_data.pop('media')
        step = StepModel.objects.create(**validated_data)

        for media in media_data:
            StepMediaModel.objects.create(step_id=step.id, **media_data)

        return step

class IngredientSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=RecipeModel.objects.all(), required=False)
    class Meta:
        model = IngredientModel
        fields = ['id', 'recipe_id', 'name', 'quantity', 'unit']
        extra_kwargs = {
            'quantity': {'required': True}
        }

class ReviewMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewMediaModel
        fields = ['id', 'interaction_id', 'media']

class InteractionSerializer(serializers.ModelSerializer):
    media = ReviewMediaSerializer(many=True, read_only=False, required=False)
    class Meta:
        model = InteractionModel
        fields = ['id', 'recipe_id', 'user_id', 'like', 'favourite', 'rating', 'comment', 'published_time', 'media']


class RecipeSerializer(serializers.ModelSerializer):
    media = RecipeMediaSerializer(many=True)
    steps = StepSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
    interactions = InteractionSerializer(many=True, required=False)


    class Meta:
        model = RecipeModel
        fields = ['id', 'user_id', 'name', 'based_on', 'total_reviews', 'total_likes', 'total_favs', 'published_time',
                  'difficulty', 'meal', 'diet', 'cuisine', 'cooking_time', 'prep_time', 'servings_num', 'media', 'steps', 'ingredients', 'interactions']

        extra_kwargs = {
            'media': {'write_only': True}, 
            'steps': {'write_only': True},
            'ingredients': {'write_only': True},
            'interactions': {'write_only': True}
        }
    # def create(self, validated_data):
    #     validated_data['user_id'] = self.context['request'].user.id
    #     steps_data = validated_data.pop('steps')
    #     media_data = validated_data.pop('media')
    #     ingredients_data = validated_data.pop('ingredients')
    #     interaction_data = validated_data.pop('interactions')

    #     recipe = RecipeModel.objects.create(**validated_data)
    #     for steps in steps_data:
    #         StepModel.objects.create(recipe_id=recipe.id, **steps_data)

    #     for media in media_data:
    #         RecipeMediaModel.objects.create(recipe_id=recipe.id, **media_data)
        
    #     for ingredient in ingredients_data:
    #         IngredientModel.objects.create(recipe_id=recipe.id, **ingredients_data)

    #     for interaction in interaction_data:
    #         InteractionModel.objects.create(recipe_id=recipe.id, **interaction_data)

    #     return recipe