# Generated by Django 4.1.7 on 2023-03-09 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_alter_recipemodel_based_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stepmediamodel',
            name='media',
            field=models.FileField(blank=True, upload_to='step-media/'),
        ),
    ]