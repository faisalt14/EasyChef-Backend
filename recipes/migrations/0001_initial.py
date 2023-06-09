# Generated by Django 4.1.7 on 2023-03-06 08:35

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('total_reviews', models.IntegerField(default=0)),
                ('total_likes', models.IntegerField(default=0)),
                ('total_favs', models.IntegerField(default=0)),
                ('published_time', models.DateTimeField(default=datetime.datetime.now)),
                ('difficulty', models.IntegerField(choices=[(0, 'Easy'), (1, 'Medium'), (2, 'Hard')])),
                ('meal', models.IntegerField(choices=[(0, 'Breakfast'), (1, 'Lunch'), (3, 'Desserts'), (4, 'Snacks'), (5, 'Other')])),
                ('diet', models.IntegerField(choices=[(0, 'Vegan'), (1, 'Vegetarian'), (2, 'Gluten-Free'), (3, 'Halal'), (4, 'Kosher'), (5, 'None')])),
                ('cuisine', models.IntegerField(choices=[(0, 'African'), (1, 'Carribean'), (2, 'East Asian'), (3, 'European'), (4, 'French'), (5, 'Italian'), (6, 'Middle-Eastern'), (7, 'North American'), (8, 'Oceanic'), (9, 'Russian'), (10, 'Spanish'), (11, 'South American'), (12, 'South Asian'), (13, 'Other')])),
                ('cooking_time', models.IntegerField()),
                ('prep_time', models.IntegerField()),
                ('servings_num', models.IntegerField()),
                ('based_on', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='based_recipe', to='recipes.recipemodel')),
                ('user_id', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeMediaModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.FileField(upload_to='recipe-media/')),
                ('recipe_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.recipemodel')),
            ],
        ),
    ]
