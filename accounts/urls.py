"""p2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
 """
from django.contrib import admin
from django.urls import path

from accounts.views import SignUpView, LoginView, LogoutView, EditProfileView, CombinedListView, IndividualListView, \
    UpdateServingSize, RemoveFromCart, EmptyShoppingCart, PublishedRecipesView, RecentRecipesView, FavouriteRecipesView, CombinedListView

from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('profile/edit/', EditProfileView.as_view()),
    path('myrecipes/published-recipes/', PublishedRecipesView.as_view()),
    path('myrecipes/recent-recipes/', RecentRecipesView.as_view()),
    path('myrecipes/favourite-recipes/', FavouriteRecipesView.as_view()), 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('combined-list/', CombinedListView.as_view()),
    path('shopping-list/', IndividualListView.as_view()),
    # path('shopping-list/recipes/', ShoppingRecipeModelView.as_view()),
    path('shopping-list/update-serving-size/<int:recipe_id>/', UpdateServingSize.as_view()),
    path('shopping-list/remove/<int:recipe_id>/', RemoveFromCart.as_view()),
    path('shopping-list/clear/', EmptyShoppingCart.as_view()),

]


