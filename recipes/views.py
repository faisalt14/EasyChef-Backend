from datetime import timedelta
from django.shortcuts import render
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import RecipeModel, IngredientModel
from recipes.serializers import RecipesSerializer, IngredientSerializer
from accounts.models import User
from accounts.serializers import UserDetailSerializer

# Create your views here.


class AllRecipes(ListAPIView):
    serializer_class = RecipesSerializer

    def get_queryset(self):
        return RecipeModel.objects.all()


class PopularRecipes(ListAPIView):
    serializer_class = RecipesSerializer

    def get_queryset(self):
        options = ['total_reviews', 'total_likes', 'total_favs']
        if self.kwargs['filter'] not in options:
            # return Response(
            #     {
            #         'Error': 'Not a valid filter. Please select a filter from the following list',
            #         'Possible Values': options
            #     }
            # )
            raise APIException("Not a valid filter. Please select a filter from the following list: "
                               "['total_reviews', 'total_likes', 'total_favs']")
        else:
            return RecipeModel.objects.all().order_by('-' + self.kwargs['filter'])

        from django.shortcuts import render

# Create your views here.
from rest_framework.exceptions import APIException
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import RecipeModel
from recipes.serializers import RecipesSerializer


class AllRecipes(ListAPIView):
    serializer_class = RecipesSerializer

    def get_queryset(self):
        return RecipeModel.objects.all()


class PopularRecipes(ListAPIView):
    serializer_class = RecipesSerializer

    def get_queryset(self):
        options = ['total_reviews', 'total_likes', 'total_favs']
        if self.kwargs['filter'] not in options:
            # return Response(
            #     {
            #         'Error': 'Not a valid filter. Please select a filter from the following list',
            #         'Possible Values': options
            #     }
            # )
            raise APIException("Not a valid filter. Please select a filter from the following list: "
                               "['total_reviews', 'total_likes', 'total_favs']")
        else:
            return RecipeModel.objects.all().order_by('-' + self.kwargs['filter'])

class SearchView(ListAPIView):
    serializer_class = RecipesSerializer
    
    def get_queryset(self):

        # Create the base search results based on simple dropdown filters
        search_results = RecipeModel.objects.filter(cuisine=int(self.request.query_params.get('cuisine'))) if (int(self.request.query_params.get('cuisine', 14)) < 14) else RecipeModel.objects.all()
        search_results = search_results.filter(diet=int(self.request.query_params.get('diet', 5))) if (int(self.request.query_params.get('diet', 6)) < 6) else search_results
        search_results = search_results.filter(meal=int(self.request.query_params.get('meal', 5))) if (int(self.request.query_params.get('meal', 6)) < 6) else search_results
        

        # Check for the search query based on the search category
        category = self.request.query_params.get('category', '')
        query = self.request.query_params.get('query', '')
        if category == 'Recipe':
            search_results = search_results.filter(name__icontains=query)
        elif category == 'Ingredients':
            search_results = search_results.filter(ingredients__name__icontains=query)
        elif category == 'User':
            search_results = search_results.filter(user_id__username__icontains=query)
        else:
            raise APIException("Not a valid search category. Please select a category from the following list: "
                               "['Recipe', 'Ingredients', 'User']")

        try:
            cooking_time = int(self.request.query_params.get('cooking_time', 0))
        except:
            raise APIException("Not a valid cooking time filter. Please select a cooking from the following list by inputting its number: "
                               "[0: None, 1: Less than 10 minutes, 2: Between 10 and 30 minutes, 3: Between 30 and 60 minutes, 4: One hour or longer]")
        # Filter by cooking time filter
        # match case would probably work better here
        if cooking_time == 0:
            return search_results
        elif cooking_time == 1:
            return search_results.filter(cooking_time__lte=timedelta(minutes=10))
        elif cooking_time == 2:
            return search_results.filter(cooking_time__lte=timedelta(minutes=30), cooking_time__gte=timedelta(minutes=10))
        elif cooking_time == 3:
            return search_results.filter(cooking_time__lte=timedelta(minutes=60), cooking_time__gte=timedelta(minutes=30))
        else:
            return search_results.filter(cooking_time__gte=timedelta(minutes=60))

class HomeView(APIView):
    serializer_class = RecipesSerializer

    def get(self, request):
        PopularSet = RecipeModel.objects.all().order_by('-total_reviews')[:6]
        BreakfastSet = RecipeModel.objects.filter(meal=0).order_by('total_favs')[:6]
        LunchSet = RecipeModel.objects.filter(meal=1).order_by('total_favs')[:6]
        DinnerSet = RecipeModel.objects.filter(meal=2).order_by('total_favs')[:6]
        return Response({'Popular' : RecipesSerializer(PopularSet, many=True).data,
                         'Breakfasts' : RecipesSerializer(BreakfastSet, many=True).data,
                         'Lunches': RecipesSerializer(LunchSet, many=True).data,
                         'Dinners': RecipesSerializer(DinnerSet, many=True).data})

class AutocompleteView(ListAPIView):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        # Get values from params, default will be 0
        category = int(self.request.query_params.get('category', '0'))
        search_query = self.request.query_params.get('query', '')
        # Set up serializers and querysets based on category, default is the IngredientModel
        if category == 1:
            self.serializer_class = RecipesSerializer
            queryset = RecipeModel.objects.all()
        elif category == 2:
            self.serializer_class = UserDetailSerializer
            queryset = User.objects.all()
            queryset = queryset.filter(username__icontains=search_query)
        else:
            queryset = IngredientModel.objects.filter(recipe_id=None)

        if search_query and category != 2:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset