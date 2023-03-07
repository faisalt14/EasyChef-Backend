# from django.shortcuts import render
# from rest_framework.generics import RetrieveAPIView, CreateAPIView, ListAPIView
# from rest_framework.views import APIView

# from recipes.models import RecipeModel, IngredientModel
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from recipes.serializers import RecipeSerializer, IngredientSerializer


# # Create your views here.

# # class RemixRecipeView(APIView):
# #     """
# #     This view is for remix recipe view
# #     """
# #     def get(self, request, *args, **kwargs):
# #         # get the id of the based_on recipe
# #         base_recipe = get_object_or_404(RecipeModel, id=kwargs['recipe_id'])
# #         return Response({})
# #         # send a response with the fields filled out except for reviews and the like


# class CreateRecipeView(CreateAPIView):
#     serializer_class = RecipeSerializer

#     def get(self, request, *args, **kwargs):
#         current_user_id = request.user.id
#         data = {'user_id': current_user_id}
#         serializer = RecipeSerializer(data=data)
#         serializer.is_valid()
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid()
#         serializer.save()
#         return Response(serializer.data)

# class IngredientAutocompleteView(ListAPIView):
#     serializer_class = IngredientSerializer
#     queryset = IngredientModel.objects.all()

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         search_query = self.request.query_params.get('query', '')
#         if search_query:
#             queryset = queryset.filter(name__icontains=search_query)
#         return queryset

