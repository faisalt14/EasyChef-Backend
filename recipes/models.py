# Create your models here.
import datetime
from django.db import models
from accounts.models import User

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
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=User.objects.first().id, related_name="recipes")
    name = models.CharField(max_length=255)
    based_on = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name="derived_recipe")
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
    servings_num = models.IntegerField()

    def __str__(self):
        return self.name

class RecipeMediaModel(models.Model):
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE, related_name="media")
    media = models.FileField(upload_to="recipe-media/")

    def __str__(self):
          return f"Media {self.id} for recipe {self.recipe_id.id}: {self.recipe_id.name}"


class StepModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - StepMediaModel for the step it applies to
    """
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE, related_name="steps")
    step_num = models.PositiveIntegerField()
    cooking_time = models.DurationField()
    prep_time = models.DurationField()
    instructions = models.CharField(max_length=225)

    def __str__(self):
        return f"Step {self.step_num} for recipe {self.recipe_id.id}: {self.recipe_id.name}"

class StepMediaModel(models.Model):
    step_id = models.ForeignKey("StepModel", on_delete=models.CASCADE, related_name="media")
    media = models.FileField(upload_to="step-media/")

    def __str__(self):
          return f"Media {self.id} for Step {self.step_id.id}"


class IngredientModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - QuantityModel for the ingredient
      - RecipeModel for search filtering
      - ShoppingQuantityModel for the ingredient
    """
    name = models.CharField(max_length=100)
    recipes = models.ManyToManyField('RecipeModel', related_name='ingredients')

    def __str__(self):
      return self.name


class QuantityModel(models.Model):
    ingredient = models.ForeignKey("IngredientModel", on_delete=models.CASCADE, related_name="ingredient_quantities")
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE, related_name="recipe_quantities")
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.name} for recipe {self.recipe_id.id} - {self.recipe_id.name}"



class InteractionModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - ReviewModel for the interaction
    """
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE, related_name="interactions")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=User.objects.first().id, related_name="interactions")
    like = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user_id.username}, {self.recipe_id.id}: {self.recipe_id.name} ({'liked' if self.like else 'not liked'}, {'favourited' if self.favourite else 'not favourited'})"


class ReviewModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - ReviewModel for the review this media belongs to
    """
    interaction_id = models.ForeignKey("InteractionModel", on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField()
    comment = models.CharField(max_length=200, blank=True, null=True)
    published_time = models.DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"Review {self.id} for interaction {self.interaction_id.id}: {self.rating} stars"


class ReviewMediaModel(models.Model):
    review_id = models.ForeignKey("ReviewModel",  on_delete=models.CASCADE, related_name="media")
    media = models.FileField(upload_to="review-media/")

    def __str__(self):
        return f"Media for review {self.review_id.id}"