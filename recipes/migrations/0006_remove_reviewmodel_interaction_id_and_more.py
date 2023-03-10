# Generated by Django 4.1.7 on 2023-03-07 04:33

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import recipes.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0005_alter_recipemodel_servings_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewmodel',
            name='interaction_id',
        ),
        migrations.RemoveField(
            model_name='ingredientmodel',
            name='recipes',
        ),
        migrations.RemoveField(
            model_name='reviewmediamodel',
            name='review_id',
        ),
        migrations.AddField(
            model_name='ingredientmodel',
            name='quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='ingredientmodel',
            name='recipe_id',
            field=models.ForeignKey(default=recipes.models.get_default_recipe_id, on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipes.recipemodel'),
        ),
        migrations.AddField(
            model_name='ingredientmodel',
            name='unit',
            field=models.CharField(default='cups', max_length=20),
        ),
        migrations.AddField(
            model_name='interactionmodel',
            name='comment',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='interactionmodel',
            name='published_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='interactionmodel',
            name='rating',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reviewmediamodel',
            name='interaction_id',
            field=models.ForeignKey(default=recipes.models.get_default_interaction_id, on_delete=django.db.models.deletion.CASCADE, related_name='media', to='recipes.interactionmodel'),
        ),
        migrations.AlterField(
            model_name='interactionmodel',
            name='recipe_id',
            field=models.ForeignKey(default=recipes.models.get_default_recipe_id, on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='recipes.recipemodel'),
        ),
        migrations.AlterField(
            model_name='interactionmodel',
            name='user_id',
            field=models.ForeignKey(default=recipes.models.get_default_user_id, on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='recipemediamodel',
            name='recipe_id',
            field=models.ForeignKey(default=recipes.models.get_default_recipe_id, on_delete=django.db.models.deletion.CASCADE, related_name='media', to='recipes.recipemodel'),
        ),
        migrations.AlterField(
            model_name='recipemodel',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='recipemodel',
            name='user_id',
            field=models.ForeignKey(default=recipes.models.get_default_user_id, on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='stepmodel',
            name='recipe_id',
            field=models.ForeignKey(default=recipes.models.get_default_recipe_id, on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='recipes.recipemodel'),
        ),
        migrations.DeleteModel(
            name='QuantityModel',
        ),
        migrations.DeleteModel(
            name='ReviewModel',
        ),
    ]