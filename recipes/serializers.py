from rest_framework import serializers
from recipes.models import RecipeModel, RecipeMediaModel, StepModel, StepMediaModel, InteractionModel, ReviewMediaModel, IngredientModel
from datetime import timedelta


class RecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeModel
        fields = ['name', 'difficulty', 'meal', 'cuisine', 'total_reviews', 'total_likes', 'total_favs']


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

class DurationField(serializers.Field):
    def to_representation(self, value):
        hours, remainder = divmod(value.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)
    
    def to_internal_value(self, value):
        if isinstance(value, str):
            hours, minutes, seconds = map(int, value.split(':'))
            return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
        return value

class StepSerializer(serializers.ModelSerializer):
    cooking_time = DurationField()
    prep_time = DurationField()
    media = StepMediaSerializer(many=True, read_only=False, required=False)

    class Meta:
        model = StepModel
        fields = ['id', 'recipe_id', 'step_num', 'cooking_time', 'prep_time', 'instructions', 'media']
        extra_kwargs = {
            'media': {'required': False, 'allow_null': True},
            'step_num': {'required': False}
        }

    def create(self, validated_data):
        media_data = validated_data.get('media', '')
        cook = validated_data.get('cooking_time', '')
        prep = validated_data.get('prep_time', '')

        if isinstance(cook, str):
            hours, minutes, seconds = map(int, cook.split(':'))
            cook = timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
            validated_data['cooking_time'] = cook

        if isinstance(prep, str):
            hours, minutes, seconds = map(int, prep.split(':'))
            prep = timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
            validated_data['prep_time'] = prep
        step = StepModel.objects.create(**validated_data)

        for media in media_data:
            StepMediaModel.objects.create(step_id=step.id, **media_data)

        return step

class IngredientSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=RecipeModel.objects.all(), required=False)
    quantity = serializers.IntegerField()
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
    cooking_time = DurationField()
    prep_time = DurationField()
    total_time = DurationField() 
    calculated_total_time = DurationField(read_only=True) 
    calculated_prep_time = DurationField(read_only=True)
    calculated_cook_time = DurationField(read_only=True)

    media = RecipeMediaSerializer(many=True, required=True)
    steps = StepSerializer(many=True, required=True)
    ingredients = IngredientSerializer(many=True, required=True)
    interactions = InteractionSerializer(many=True, required=False)

    name = serializers.CharField(required=True)
    difficulty = serializers.IntegerField(required=True, allow_null=False)
    meal = serializers.IntegerField(required=True, allow_null=False)
    diet = serializers.IntegerField(required=True, allow_null=False)
    cuisine = serializers.IntegerField(required=True, allow_null=False)
    servings_num = serializers.IntegerField(required=True, allow_null=False)

    class Meta:
        model = RecipeModel
        fields = ['id', 'user_id', 'name', 'based_on', 'total_reviews', 'total_likes', 'total_favs', 'published_time',
                  'difficulty', 'meal', 'diet', 'cuisine', 'total_time', 'cooking_time', 'prep_time', 'calculated_total_time', 'calculated_prep_time', 'calculated_cook_time', 
                  'servings_num', 'media', 'steps', 'ingredients', 'interactions']

        extra_kwargs = {
            'media': {'write_only': True}, 
            'steps': {'write_only': True},
            'ingredients': {'write_only': True},
            'interactions': {'write_only': True},
            'name': {'required': True},
        }
