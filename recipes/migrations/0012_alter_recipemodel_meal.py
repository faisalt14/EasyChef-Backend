# Generated by Django 4.1.7 on 2023-03-10 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_alter_recipemodel_meal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipemodel',
            name='meal',
            field=models.IntegerField(choices=[(0, 'Breakfast'), (1, 'Lunch'), (2, 'Dinner'), (3, 'Desserts'), (4, 'Snacks'), (5, 'Other')]),
        ),
    ]
