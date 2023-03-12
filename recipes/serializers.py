from rest_framework import serializers


from recipes.models import RecipeModel, IngredientModel, RecipeMediaModel

class RecipeMediaSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=RecipeModel.objects.all(), required=False)
    class Meta:
        model = RecipeMediaModel
        fields = ['id', 'recipe_id', 'media']

class RecipesSerializer(serializers.ModelSerializer):
    media = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = RecipeModel
        fields = ['id', 'name', 'difficulty', 'meal', 'diet', 'cuisine', 'cooking_time', 'avg_rating', 'total_reviews', 'total_likes', 'total_favs', 'media']
    
    def get_media(self, obj):
        media = obj.media.first()
        if media:
            serializer = RecipeMediaSerializer(media)
            return serializer.data['media']
        return None

class IngredientSerializer(serializers.ModelSerializer):
    recipe_id = serializers.PrimaryKeyRelatedField(queryset=RecipeModel.objects.all(), required=False)
    quantity = serializers.IntegerField()
    class Meta:
        model = IngredientModel
        fields = ['id', 'recipe_id', 'name', 'quantity', 'unit']
        extra_kwargs = {
            'quantity': {'required': True}
        }



