# from rest_framework import serializers
# from .models import RecipeModel, RecipeMediaModel, StepModel, StepMediaModel, QuantityModel, InteractionModel, ReviewModel, ReviewMediaModel, IngredientModel

# class RecipeMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RecipeMediaModel
#         fields = ['id', 'recipe_id', 'media']

# class StepMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StepMediaModel
#         fields = ['id', 'step_id', 'media']

# class StepSerializer(serializers.ModelSerializer):
#     media = StepMediaSerializer(many=True, read_only=False)

#     class Meta:
#         model = StepModel
#         fields = ['id', 'recipe_id', 'step_num', 'cooking_time', 'prep_time', 'instructions', 'media']


# class IngredientSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IngredientModel
#         fields = ['id', 'name', 'recipes']

# class QuantitySerializer(serializers.ModelSerializer):
#     ingredient = serializers.StringRelatedField()

#     class Meta:
#         model = QuantityModel
#         fields = ['ingredient', 'quantity', 'unit']

# class InteractionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InteractionModel
#         fields = ['id', 'recipe_id', 'user_id', 'like', 'favourite']


# class ReviewMediaSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ReviewMediaModel
#         fields = ['id', 'review', 'media']


# class ReviewSerializer(serializers.ModelSerializer):
#     interaction = InteractionSerializer(read_only=True)
#     media = ReviewMediaSerializer(many=True, read_only=True)

#     class Meta:
#         model = ReviewModel
#         fields = ['id', 'interaction', 'rating', 'comment', 'published_time', 'media']


# class RecipeSerializer(serializers.ModelSerializer):
#     media = RecipeMediaSerializer(many=True, read_only=False)
#     steps = StepSerializer(many=True, read_only=False)
#     ingredients = QuantitySerializer(source='recipe_quantities', many=True, read_only=False)


#     class Meta:
#         model = RecipeModel
#         fields = ['id', 'user_id', 'name', 'based_on', 'total_reviews', 'total_likes', 'total_favs', 'published_time',
#                   'difficulty', 'meal', 'diet', 'cuisine', 'cooking_time', 'prep_time', 'servings_num', 'media', 'steps', 'ingredients']

