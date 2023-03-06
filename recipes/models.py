# Create your models here.
import datetime
from django.db import models
from django.contrib.auth.models import User

class RecipeModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - StepModel for steps
      - RecipeMediaModel for the displayed images/videos at top
      - QuantityModel for ingredients and Quantities
      - ReviewModel for the review
      - 'self' for “based on” recipes
    """
    # change this to reference custom UserModel
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=User.objects.first().id)
    name = models.CharField(max_length=255)
    based_on = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    total_reviews = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    total_favs = models.IntegerField(default=0)
    published_time = models.DateTimeField(default=datetime.datetime.now)
    difficulty_choices = [
          (0, 'Easy'),
          (1, 'Medium'),
          (2, 'Hard'),
      ]
    meal_choices = [(0, "Breakfast"), (1, "Lunch"), (3, "Desserts"), (4, "Snacks"), (5, "Other")]
    diet_choices = [(0, "Vegan"), (1, "Vegetarian"), (2, "Gluten-Free"), (3, "Halal"), (4, "Kosher"), (5, "None") ]
    cuisine_choices = [(0, "African"), (1, "Carribean"), (2, "East Asian"), (3, "European"), (4, "French"), (5, "Italian"), (6, "Middle-Eastern"), (7, "North American"),
    (8, "Oceanic"), (9, "Russian"), (10, "Spanish"), (11, "South American"),  (12, "South Asian"), (13, "Other")]
    difficulty = models.IntegerField(choices=difficulty_choices)
    meal = models.IntegerField(choices=meal_choices)
    diet = models.IntegerField(choices=diet_choices)
    cuisine = models.IntegerField(choices=cuisine_choices)
    cooking_time = models.DurationField()
    prep_time = models.DurationField()
    servings_num = models.DurationField()

    def __str__(self):
        return self.name

class RecipeMediaModel(models.Model):
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE)
    media = models.FileField(upload_to="recipe-media/")

class StepModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - StepMediaModel for the step it applies to
    """
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE)
    step_num = models.PositiveIntegerField()
    cooking_time = models.DurationField()
    prep_time = models.DurationField()
    instructions = models.CharField(max_length=225)

class StepMediaModel(models.Model):
    step_id = models.ForeignKey("StepModel", on_delete=models.CASCADE, related_name="step_media")
    media = models.FileField(upload_to="step-media/")

class IngredientModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - QuantityModel for the ingredient
      - RecipeModel for search filtering
      - ShoppingQuantityModel for the ingredient

    An example class of how to use the IngredientModel:
    We can retrieve all the recipes that use a particular ingredient by doing:
    >>> ingredient = IngredientModel.objects.get(...)
    >>> recipes = ingredient.recipes.all()

    And we can retrieve all the ingredients for a recipe by doing: 
    >>> recipe = RecipeModel.objects.get(...)
    >>> ingredients = recipe.ingredients.all()
    """
    name = models.CharField(max_length=100)
    recipes = models.ManyToManyField('RecipeModel', related_name='ingredients')


class QuantityModel(models.Model):
    ingredient = models.ForeignKey("IngredientModel", on_delete=models.CASCADE)
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)


class InteractionModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - ReviewModel for the interaction
    """
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE, related_name="recipe")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=User.objects.first().id)
    like = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)


class ReviewModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - ReviewModel for the review this media belongs to
    """
    interaction_id = models.ForeignKey("InteractionModel", on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.CharField(max_length=200, blank=True, null=True)
    published_time = models.DateTimeField(default=datetime.datetime.now)


class ReviewMediaModel(models.Model):
    review_id = models.ForeignKey("ReviewModel",  on_delete=models.CASCADE)
    media = models.FileField(upload_to="review-media/")

