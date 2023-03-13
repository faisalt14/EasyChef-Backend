# Create your models here.
import datetime
from django.utils import timezone
from django.db import models
from accounts.models import User

def get_default_user_id():
    user = User.objects.first()
    if user:
        return user.id
    return None


def get_default_recipe_id():
    recipe = RecipeModel.objects.first()
    if recipe:
        return recipe.id
    return None

def get_default_interaction_id():
    interac = InteractionModel.objects.first()
    if interac:
        return interac.id
    return None


class RecipeModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - StepModel for steps
      - RecipeMediaModel for the displayed images/videos at top
      - IngredientModel for ingredients and Quantities
      - ReviewModel for the review
      - 'self' for “based on” recipes
    """
    # change this to reference custom UserModel
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=get_default_user_id, related_name="recipes")
    name = models.CharField(max_length=100)
    based_on = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="derived_recipe")
    total_reviews = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    total_favs = models.IntegerField(default=0)
    avg_rating = models.FloatField(default=0)
    published_time = models.DateTimeField(default=timezone.now)
    difficulty_choices = [
          (0, 'Easy'),
          (1, 'Medium'),
          (2, 'Hard'),
      ]
    meal_choices = [(0, "Breakfast"), (1, "Lunch"), (2, "Dinner"), (3, "Desserts"), (4, "Snacks"), (5, "Other")]
    diet_choices = [(0, "Vegan"), (1, "Vegetarian"), (2, "Gluten-Free"), (3, "Halal"), (4, "Kosher"), (5, "None") ]
    cuisine_choices = [(0, "African"), (1, "Carribean"), (2, "East Asian"), (3, "European"), (4, "French"), (5, "Italian"), (6, "Middle-Eastern"), (7, "North American"),
    (8, "Oceanic"), (9, "Russian"), (10, "Spanish"), (11, "South American"),  (12, "South Asian"), (13, "Other")]
    difficulty = models.IntegerField(choices=difficulty_choices)
    meal = models.IntegerField(choices=meal_choices)
    diet = models.IntegerField(choices=diet_choices)
    cuisine = models.IntegerField(choices=cuisine_choices)
    cooking_time = models.DurationField()
    prep_time = models.DurationField()
    calculated_total_time = models.DurationField(default=datetime.timedelta(hours=0, minutes=0))
    calculated_cook_time = models.DurationField(default=datetime.timedelta(hours=0, minutes=0))
    calculated_prep_time = models.DurationField(default=datetime.timedelta(hours=0, minutes=0))
    total_time = models.DurationField(default=datetime.timedelta(hours=0, minutes=0))
    servings_num = models.IntegerField()

    def __str__(self):
        return self.name + ' [' + str(self.id) + ']'

    def save(self, *args, **kwargs):
        if self.cooking_time != None and self.prep_time != None:
            self.total_time = self.cooking_time + self.prep_time
        self.calculated_total_time = self.calculated_cook_time + self.calculated_prep_time
        super().save(*args, **kwargs)
    
    def update_interactions(self):
        self.total_likes = len(self.interactions.filter(like=True))
        self.total_favs = len(self.interactions.filter(favourite=True))
        self.total_reviews = len(self.interactions.filter(rating__gt=0))
        
        acc = 0
        for interaction in self.interactions.all():
            if interaction.rating > 0:
                acc += interaction.rating
        if self.total_reviews:
            self.avg_rating = round(acc/self.total_reviews, 1)
        else:
            self.avg_rating = 0
        self.save()
        

class RecipeMediaModel(models.Model):
    recipe_id = models.ForeignKey(RecipeModel, on_delete=models.CASCADE, related_name="media", blank=True, null=True)
    media = models.FileField(upload_to="recipe-media/")

    def __str__(self):
          return f"{self.id}: Media {self.id}"


class StepModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - StepMediaModel for the step it applies to
    """
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE, related_name="steps", default=None, blank=True, null=True)
    step_num = models.PositiveIntegerField(default=0)
    cooking_time = models.DurationField()
    prep_time = models.DurationField()
    instructions = models.CharField(max_length=225)

    def __str__(self):
        if self.recipe_id is not None:
            return f"{self.id} - Step {self.step_num} for recipe {self.recipe_id.id}: {self.recipe_id.name}"
        else:
            return f"{self.id} - Step {self.step_num} for an unspecified recipe"

class StepMediaModel(models.Model):
    step_id = models.ForeignKey("StepModel", on_delete=models.CASCADE, related_name="media")
    media = models.FileField(upload_to="step-media/", blank=True)

    def __str__(self):
          return f"Media {self.id} for Step {self.step_id.id}"


class IngredientModel(models.Model):
    """
    Foreign Key To Keep Track Of:
      - RecipeModel for search filtering
    """
    recipe_id= models.ForeignKey('RecipeModel', on_delete=models.CASCADE, related_name='ingredients', default=None, blank=True, null=True)
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=20, default="cups")
    
    def __str__(self):
      return f"{self.name}: {self.id}" 

class InteractionModel(models.Model):
    """
    Foreign Keys To Keep Track Of:
      - ReviewMediaModel for the interaction
    """
    recipe_id = models.ForeignKey("RecipeModel", on_delete=models.CASCADE, related_name="interactions", default=get_default_recipe_id)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=get_default_user_id, related_name="interactions")
    like = models.BooleanField(default=False)
    favourite = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(default=0)
    comment = models.CharField(max_length=200, blank=True, null=True)
    published_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user_id.username}, {self.recipe_id.id}: {self.recipe_id.name} ({'liked' if self.like else 'not liked'}, {'favourited' if self.favourite else 'not favourited'})"

class ReviewMediaModel(models.Model):
    interaction_id = models.ForeignKey("InteractionModel",  on_delete=models.CASCADE, related_name="media", default=get_default_interaction_id)
    media = models.FileField(upload_to="review-media/")

    def __str__(self):
        return f"Media for review {self.interaction_id.id}"
